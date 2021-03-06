"""
/*******************************************************************************
Copyright 2021
Steward Observatory Engineering & Technical Services, University of Arizona
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
*******************************************************************************/
Author: Nestor Garcia (Nestor212@email.arizona.edu)
Brief: Sparkplug/MQTT client to communicate with and command Thermistor Mux module. 
Capable of reading data published from them, and publishing commands to them.
Adapted from SOML VCM firmware https://github.com/Steward-Observatory-ETS/soml_cf_vcm.git
Adapted from python client example at https://github.com/eclipse/tahu
"""

from distutils.log import error
from multiprocessing.connection import wait
from os import times
import time
import datetime
import threading
import sys
import random
import csv
from typing import Any

import paho.mqtt.client as mqtt
from sparkplug_b import *

# Application constants
APP_VERSION             = '2.0'
COMMS_VERSION           = 2
COMMS_VERSION_METRIC    = 'Properties/Communications Version'
BIRTH_DEATH_SEQ_METRIC  = 'bdSeq'
NODE_ID                 = 'TEC'
NUM_MODULES             = 6
NUM_TEC                 = 12
DEFAULT_BROKER_URL      = 'localhost'
DEFAULT_BROKER_PORT     = 1884
DEFAULT_MODULE_ID       = 0
SHOW_OPTIONS            = [ 'none', 'errors', 'topic', 'changed', 'all' ] 
CAL_OPTIONS             = [ 'temp1', 'temp2', 'status', 'clear' ]
DATA_OPTIONS            = [ 'seebeck', 'temp' ]

module_is_alive         = False
compatible_version      = False
gui_controls_created    = False
message_seq             = 0
cal_started             = False
cal_status              = False
cal_INW                 = False
option_data             = False

date_string = datetime.datetime.now().strftime( '%Y-%m-%d' )
LOG_FILENAME = f'TEC_test_log_{date_string}.csv'

# Convert a timestamp in milliseconds to a string
def timestamp_str( timestamp ):
    if timestamp == None:
        return f'{timestamp}'
    if isinstance( timestamp, str ):
        # Timestamp is already a string (in case we call this function twice)
        return timestamp
    return datetime.datetime.fromtimestamp( timestamp / 1000 ).isoformat( ' ', timespec = 'milliseconds' )

class MetricSpec:
    def __init__( self, device, name, display_name, log_data ):
        self.device = device
        self.name = name
        if display_name == 'strip to /':
            display_name = name.split( '/' )[ -1 ]
        self.display_name = display_name
        self.log_data = log_data
        self.alias = None
        self.value = None
        self.value_str = f'{self.value}'
        self.timestamp = timestamp_str( None ) 

Metrics = (
    [ MetricSpec( None, 'bdSeq',                                      'strip to /', False ) ] +
    [ MetricSpec( None, 'Properties/Calibration Status',              'strip to /', False ) ] +
    [ MetricSpec( None, 'Properties/Calibration INW',                 'strip to /', False ) ] +
    [ MetricSpec( None, 'Properties/Data Selection',                  'strip to /', True ) ] +
    [ MetricSpec( None, 'Properties/Units',                           'strip to /', True  ) ] +
    [ MetricSpec( None, 'Properties/Firmware Version',                'strip to /', True  ) ] +
    [ MetricSpec( None, 'Properties/Communications Version',          'strip to /', False ) ] +
    [ MetricSpec( None, 'Node Control/Reboot',                        'strip to /', False ) ] +
    [ MetricSpec( None, 'Node Control/Rebirth',                       'strip to /', False ) ] +
    [ MetricSpec( None, 'Node Control/Calibration Temperature 1',     'strip to /', False ) ] +
    [ MetricSpec( None, 'Node Control/Calibration Temperature 2',     'strip to /', False ) ] +
    [ MetricSpec( None, 'Node Control/Clear Cal Data',                'strip to /', False ) ] +
    [ MetricSpec( None, f'Inputs/Power Channel{channel + 1}',             'strip to /', True  ) for channel in range( NUM_TEC ) ] +
    [ MetricSpec( None, f'Outputs/Direction Channel{channel + 1}',        'strip to /', True  ) for channel in range( NUM_TEC ) ] +
    [ MetricSpec( None, f'Outputs/Data Channel{channel + 1}',             'strip to /', True  ) for channel in range( NUM_TEC ) ] 
    )

# Reset the aliases and/or values for all the metrics of the specified device
def reset_metrics( device, reset_alias = True ):
    for metric in Metrics:
        if metric.device == device:
            if reset_alias:
                metric.alias = None
            metric.value = None
            metric.timestamp = None

# Reset the aliases and values for all known metrics
def reset_all_metrics():
    reset_metrics( None )

# Find the matching metric in the Metrics list, matching by name if specified,
# otherwise by alias
def find_metric( device, name = None, alias = None ):
    for metric in Metrics:
        if metric.device == device:
            if name != None and name != "":
                if metric.name == name:
                    return metric
            elif alias != None and metric.alias == alias:
                return metric
    raise ValueError

# Update the values of the metrics in the Metrics list from the payload metrics
def update_metrics( device, payload, set_alias = False ):
    for metric in payload.metrics:
        try:
            if set_alias:
                metric_spec = find_metric( device, metric.name )
                metric_spec.alias = metric.alias
            else:
                metric_spec = find_metric( device, metric.name, metric.alias )

            if metric.datatype == MetricDataType.Boolean:
                metric_spec.value = metric.boolean_value
            elif metric.datatype == MetricDataType.Int64:
                metric_spec.value = metric.long_value
            elif metric.datatype == MetricDataType.UInt64:
                metric_spec.value = metric.long_value
            elif metric.datatype == MetricDataType.Float:
                metric_spec.value = metric.float_value
            elif metric.datatype == MetricDataType.String:
                metric_spec.value = metric.string_value
            else:
                report( f'Unexpected data type {metric.datatype} for {metric_spec.name}', error = True )
                continue
            metric_spec.timestamp = timestamp_str( metric.timestamp )
        except ValueError:
            report( f'Unrecognized metric: device={device}, name="{metric.name}", alias={metric.alias}', error = True )

# Display how this program should be called, then exit
def show_usage():
    print( f'Thermo_Electric Controller Client v{APP_VERSION}' )
    print( f'Usage: {sys.argv[ 0 ]} [no_gui] [broker=[BROKER_IP][=BROKER_PORT]] [module=MODULE_ID] [reboot] [show=SHOW_WHAT] [log] [exit]' )
    print( f'where no_gui = run the command-line interface instead of the GUI' )
    print( f'      BROKER_IP = hostname or IP address of MQTT broker (default {DEFAULT_BROKER_URL})' )
    print( f'      BROKER_PORT = port number of MQTT broker (default {DEFAULT_BROKER_PORT})' )
    print( f'      MODULE_ID = the Thermistor Mux module number to contact (0-{NUM_MODULES - 1}, default {DEFAULT_MODULE_ID})' )
    print( f'      reboot = send the Reboot command to the module' )
    print( f'      show SHOW_WHAT = what to display on the command-line interface when a message is received, where SHOW_WHAT is one of:' )
    print( f'          none = don\'t display anything' )
    print( f'          errors = just display errors in incoming messages' )
    print( f'          topic = just display the message topic and errors' )
    print( f'          changed = display the message topic and only those metrics it contains (the default)' )
    print( f'          all = display the message topic and all the metrics from this module' )
    print( f'      log = log inbound data messages to a CSV file with filename thermistorMux_test_log_DATE.csv' )
    print( f'      data = toggle between displaying Seebeck voltage or Thermistor Temperature' )
    print( f'      exit = exit as soon as command-line commands are issued' )
    sys.exit()

# Display a diagnostic message.  Optional parameters indicate whether to mark it
# as an error and whether to display it regardless of the current Show setting.
def report( msg, error = False, always = False ):
    if not gui_controls_created:
        if not always:
            if option_show == 'none':
                # Don't display any messages
                return
            if option_show == 'errors' and not error:
                # Don't display any non-error messages
                return
        if error:
            msg = '*** ' + msg + ' ***'
        print( msg )
    #else:
        ### Causes segmentation fault?
        ###if error:
        ###    diagnostic_text.setCurrentCharFormat( error_format )
        #diagnostic_text.appendPlainText( msg )
        #diagnostic_text.centerCursor()
        ###diagnostic_text.setCurrentCharFormat( normal_format )

# Return the topic for a particular node message
def node_topic( module_id, message_type ):
    return f'spBv1.0/VI/{message_type}/{NODE_ID}{module_id}'


# Change which Thermistor Mux module we're communicating with
def set_module_topics( new_module_id ):
    # Set the topics for the new Thermistor Mux module
    global NODE_BIRTH_TOPIC
    NODE_BIRTH_TOPIC = node_topic( new_module_id, 'NBIRTH' )
    global NODE_DEATH_TOPIC
    NODE_DEATH_TOPIC = node_topic( new_module_id, 'NDEATH' )
    global NODE_DATA_TOPIC
    NODE_DATA_TOPIC  = node_topic( new_module_id, 'NDATA' )
    global NODE_CMD_TOPIC
    NODE_CMD_TOPIC   = node_topic( new_module_id, 'NCMD' )

def subscribe_data( client ):
    client.subscribe( NODE_BIRTH_TOPIC )
    client.subscribe( NODE_DEATH_TOPIC )
    client.subscribe( NODE_DATA_TOPIC )

def unsubscribe_data( client ):
    client.unsubscribe( NODE_BIRTH_TOPIC )
    client.unsubscribe( NODE_DEATH_TOPIC )
    client.unsubscribe( NODE_DATA_TOPIC )


# Switch to a different module
def change_module( module_id, client ):

    try:
        module_id = int( module_id )
    except ValueError:
        report( f'Invalid MODULE ID, must be an integer: "{module_id}"', error = True, always = True )
        return False
    if module_id < 0 or module_id >= NUM_MODULES:
        report( f'MODULE ID out of range 0 to {NUM_MODULES - 1}: {module_id}', error = True, always = True )
        return False

    # Unsubscribe from messages from the old module before changing topics
    if client != None:
        unsubscribe_data( client )

    # Set the topics for the new module
    set_module_topics( module_id )

    # Connect to the new module
    connect_to_module( client )

    # Report the change (unless this is the initial call)
    if client != None:
        report( f'Switching to module {module_id}', always = True )

    # Success
    return True

# Connect to the module
def connect_to_module( client ):
    global module_is_alive
    global compatible_version

    # The module is assumed dead and using an incompatible interface until we
    # receive its NBIRTH message
    module_is_alive    = False
    compatible_version = False

    # Reset the aliases and values for all the known metrics
    reset_all_metrics()

    # Establish communications with the module
    if client != None:
        # Subscribe to messages from the module
        subscribe_data( client )

        # Ask the module for its list of supported metrics
        request_rebirth()

def client_loop():
    while not close_thread:
        time.sleep( 0.1 )
        client.loop()

def on_connect( client, userdata, flags, rc ):
    if rc == 0:
        report( f'Connected with result code {rc}', always = True )
    else:
        report( f'Failed to connect with result code {rc}', error = True, always = True )
        sys.exit()

    # Connect to the new module.  Doing this in on_connect() means that if we
    # lose the connection and reconnect then subscriptions will be renewed and
    # the Rebirth command will be reissued.
    connect_to_module( client )


# Callback called when an MQTT message is received
def on_message( client, userdata, msg ):
    global module_is_alive
    global compatible_version
    global cal_started

    if option_no_GUI:
        # Insert blank lines to separate the message from the CLI prompt
        report( f'\n' )
    report( f'Message received: {msg.topic}' )

    payload = sparkplug_b_pb2.Payload()
    try:
        payload.ParseFromString( msg.payload )
    except:
        report( f'Could not parse "{msg.topic}" message', error = True, always = False )
        return

    if option_no_GUI and option_show == 'all':
        report( f'   timestamp = {timestamp_str( payload.timestamp )}' )
        report( f'   seq = {payload.seq}' )
        report( f'   num_metrics = {len( payload.metrics )}' )

    # Check the message seq number
    check_message_sequence( msg.topic, payload )

    # Process the different types of messages
    if msg.topic == NODE_BIRTH_TOPIC:
        module_is_alive = True

        # Reset the aliases and values for all the known metrics
        reset_all_metrics()

        # Check that the module is using a compatible communications interface
        if not check_comms_version( payload ):
            return

        # Report if the Birth/Death Sequence number isn't included
        check_birth_death_sequence( payload, is_expected = True, must_match = False )

        # Update the values of the node metrics
        update_metrics( None, payload, set_alias = True )
        display_metrics( msg.topic, payload, option_log )

        if not option_no_GUI:
            set_labels()

    elif not module_is_alive:
        report( 'Module is dead, message ignored', error = True )
        return
    elif not compatible_version:
        report( 'Module communications version is incompatible, message ignored', error = True )
        return
    elif msg.topic == NODE_DATA_TOPIC:
        # Report if Birth/Death Sequence number is specified
        check_birth_death_sequence( payload, is_expected = False, must_match = False )

        # Update the values of the node metrics
        update_metrics( None, payload, set_alias = False )
        display_metrics(msg.topic, payload, option_log )
    elif msg.topic == NODE_DEATH_TOPIC:
        # Report if Birth/Death Sequence number doesn't match the last NBIRTH
        check_birth_death_sequence( payload, is_expected = True, must_match = True )

        # Update the values of any node metrics in the NDEATH payload
        update_metrics( None, payload, set_alias = False )
        display_metrics( msg.topic, payload, option_log )

        module_is_alive = False
    else:
        report( f'Unknown message received: {msg.topic}, with {len( payload.metrics )} metrics', error = True )


# Check the communications version in the received payload and return True if
# it's compatible with this program, or False if it isn't
def check_comms_version( payload ):
    global compatible_version
    compatible_version = False
    for metric in payload.metrics:
        if metric.name == COMMS_VERSION_METRIC:
            if metric.long_value != COMMS_VERSION:
                report( f'Module is using an incompatible communications version: {metric.long_value} instead of {COMMS_VERSION}', error = True )
                if compatible_version:
                    report( f'Multiple conflicting {COMMS_VERSION_METRIC} metrics in NBIRTH message', error = True )
                compatible_version = False
                return False
            compatible_version = True
    if not compatible_version:
        report( f'No {COMMS_VERSION_METRIC} metric in NBIRTH message', error = True )
        return False

    # The module's communications version is compatible
    return True

# Report if the message sequence number in the payload isn't as expected:
# either it was included when it shouldn't have been (or vice versa), or it
# didn't have the expected value.
def check_message_sequence( topic, payload ):
    if topic == NODE_DEATH_TOPIC:
        # NDEATH message shouldn't have a seq number
        if payload.seq != 0:
            report( f'Unexpected seq (= {payload.seq}) in NDEATH message', error = True )
            return False
        else:
            return True

    # All other messages should have a seq number
    if payload.seq == None:
        report( f'No seq in message', error = True )
        return False

    # Remember this message sequence number
    global message_seq
    prev_seq = message_seq
    message_seq = payload.seq

    if topic == NODE_BIRTH_TOPIC:
        # NBIRTH message should have a seq number of zero
        if message_seq != 0:
            report( f'seq (= {message_seq}) in NBIRTH message should be 0', error = True )
            return False
    else:
        # Other messages should have a seq number one greater than the previous message
        next_seq = prev_seq + 1
        if next_seq > 255:
            next_seq = 0
        if message_seq != next_seq:
            report( f'seq (= {message_seq}) in message should be {next_seq} (previous = {prev_seq})', error = True )
            return False

    # Seq number is as expected
    return True

# Report if the Birth/Death Sequence number in the payload isn't as expected:
# either it was included when it shouldn't have been (or vice versa), or it
# changed value but shouldn't have.
def check_birth_death_sequence( payload, is_expected, must_match ):
    # Get the most recent bdSeq value
    try:
        metric_spec = find_metric( None, BIRTH_DEATH_SEQ_METRIC )
    except ValueError:
        report( f'Could not find "{BIRTH_DEATH_SEQ_METRIC}" in metric list', error = True, always = True )
        return False

    # Get the value from the payload
    payload_bdseq = None
    for metric in payload.metrics:
        if metric.name == BIRTH_DEATH_SEQ_METRIC:
            if payload_bdseq != None:
                report( f'Multiple {BIRTH_DEATH_SEQ_METRIC} metrics in message', error = True )
                return False
            if metric.long_value == None:
                report( f'Empty value for {BIRTH_DEATH_SEQ_METRIC} metric in message', error = True )
                return False
            payload_bdseq = metric.long_value

    # Check that the metric was/was not in the payload as expected
    if not is_expected:
        if payload_bdseq != None:
            report( f'Unexpected {BIRTH_DEATH_SEQ_METRIC} metric (= {payload_bdseq}) in message', error = True )
            return False
        # Birth/Death Sequence number is not in the payload, as expected
        return True
    if is_expected and payload_bdseq == None:
        report( f'No {BIRTH_DEATH_SEQ_METRIC} metric in message', error = True )
        return False

    # Check that the value matches if it should
    if must_match and payload_bdseq != metric_spec.value:
        report( f'{BIRTH_DEATH_SEQ_METRIC} metric mismatch: payload = {payload_bdseq}, previous = {metric_spec.value}', error = True )
        return False

    # Birth/Death Sequence number is as expected
    return True

# Display and/or log the values of the metrics
def display_metrics( topic, payload, save_to_log ):
    global option_data
    global calibrated
    global calibrationINW

    # Get the measurement units value
    units = '?'
    try:
        metric_spec = find_metric( None, 'Properties/Units' )
        if metric_spec.value != None:
            units = metric_spec.value
    except ValueError:
        pass
    try:
        metric_spec = find_metric( None, 'Properties/Data Selection' )
        if metric_spec.value != None:
            option_data = metric_spec.value
    except ValueError:
        pass
    try:
        metric_spec = find_metric( None, 'Properties/Calibration Status' )
        if metric_spec.value != None:
            calibrated = metric_spec.value_str = metric_spec.value 
    except ValueError:
        pass
    try:
        metric_spec = find_metric( None, 'Properties/Calibration INW' )
        if metric_spec.value != None:
            calibrationINW = metric_spec.value_str = metric_spec.value
    except ValueError:
        pass

    # Set the value string for each metric
    for metric in Metrics:
        for channel in range(NUM_TEC):
            if metric.value == None:
                metric.value_str = f'{metric.value}'
                break
            elif (metric.name == ( f'Inputs/Power Channel{channel + 1}')): # for channel in range(12)):
                metric.value_str = f'{metric.value:0.2f}'
                break
            elif (metric.name == ( f'Outputs/Direction Channel{channel + 1}')): # for channel in range(12)):
                metric.value_str = f'{metric.value}'
                break
            elif (metric.name == ( f'Outputs/Data Channel{channel + 1}')): # for channel in range(12)):
                if option_data: 
                    metric.display_name = f'Thermistor Temperature{channel + 1}'
                    metric.value_str = f'{metric.value:.2f} ??C'
                else: 
                    metric.display_name = f'Seebeck Voltage{channel + 1}'
                    metric.value_str = f'{metric.value:.2f} mV'
                break
            else:
                metric.value_str = f'{metric.value}'
                #report(f'Unk: {metric.value_str}')

        if option_no_GUI:
            if option_show in [ 'changed', 'all' ]:
                show_data_on_command_line( payload )
        else:
            show_data_on_GUI(metric)
    if save_to_log:
        log_data_to_CSV( payload.timestamp, topic )

def show_data_on_command_line( payload ):
    global option_data

    # If we're only displaying the metrics in the latest payload, build a list
    # of their names and aliases
    show_all = ( option_show == 'all' )
    if not show_all:
        payload_metric_names = []
        payload_metric_aliases = []
        for metric in payload.metrics:
            payload_metric_names.append( metric.name )
            payload_metric_aliases.append( metric.alias )

    # Print out the desired metrics
    for metric in Metrics:
        # If we're only displaying the metrics in the latest payload, skip this
        # metric if it isn't in the payload
        if not show_all:
            if ( metric.name  not in payload_metric_names and
                 metric.alias not in payload_metric_aliases ):
                continue
        print( f'{metric.display_name} at {metric.timestamp} = {metric.value_str}' )

# Display current metric values on the GUI
def show_data_on_GUI(metric):
    if not gui_controls_created:
        report( 'GUI controls not created - metrics not displayed', error = True, always = True )
        return

    for tec in range(NUM_TEC):
        tec_widgets[ tec  ].show( metric )
    

def log_data_to_CSV( timestamp, topic ):
    field_names = []
    row_values = []
    field_names.append( 'TIMESTAMP' )
    row_values.append( timestamp_str( timestamp ) )
    module_id = topic.split( '/' )[ -1 ]
    field_names.append( 'MODULE_ID' )
    row_values.append( module_id )
    for metric in Metrics:
        if metric.log_data:
            field_names.append( metric.display_name )
            row_values.append( metric.value_str )
    try:
        with open( LOG_FILENAME, mode = 'a+', newline = '' ) as log_file:
            log_writer = csv.writer( log_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL )
            if log_file.tell() == 0:
                log_writer.writerow( field_names )
            log_writer.writerow( row_values )
    except Exception as e:
        report( f'CSV Log: error occurred: {e}', error = True, always = True )

# Return a payload to send an NCMD or DCMD message
# Note: no seq number on CMD messages
def get_cmd_payload():
    payload = sparkplug_b_pb2.Payload()
    payload.timestamp = int( round( time.time() * 1000 ) )
    return payload

# Add a metric to the payload using the alias matching the given name.  If the
# alias can't be found, use the name instead of the alias.
def add_metric_as_alias( payload, device, metric_name, metric_type, metric_value ):
    metric_alias = None
    metric = find_metric( device, metric_name )
    if metric.alias != None:
        # Found the alias for the metric, so use that instead of its name
        metric_name = None
        metric_alias = metric.alias
    addMetric( payload, metric_name, metric_alias, metric_type, metric_value )

# Send an NCMD message with a single Boolean metric set to True
def send_simple_node_command( metric_name, value ):
    try:
        payload = get_cmd_payload()
        add_metric_as_alias( payload, None, metric_name, MetricDataType.Boolean, value )
        byte_array = bytearray( payload.SerializeToString() )
        client.publish( NODE_CMD_TOPIC, byte_array, 0, False )
        return True
    except ValueError:
        report( f'Unrecognized metric: "{metric_name}"', error = True, always = True )
        return False

# Ask the node to send out its birth messages
def request_rebirth():
    if send_simple_node_command( 'Node Control/Rebirth', True ):
        report('Rebirth requested')

# Ask the node to reboot
def reboot_module():
    if send_simple_node_command( 'Node Control/Reboot', True ):
        report( 'Module commanded to reboot', always = True )

# Add a metric to the payload to set the voltage on a TEC
def add_cal_temp_metric( payload, cal_temp, tempNum ):
    #if cal_temp < 0 or cal_temp >= 100:
    #    report( f'Calibration temperature out of range, must be 0 to 100 degrees Celsius.', error = True, always = True )
    #    return False
    cal_temp = float (cal_temp)
    try:
        add_metric_as_alias( payload, None, f'Node Control/Calibration Temperature {tempNum}', MetricDataType.Float, cal_temp )
    except ValueError:
        report( f'Unrecognized metric: "Node Control/Calibration Temperature {tempNum}', error = True, always = True )
        return False
    return True

def send_cal_command(temp1, temp2, clear):

    if temp1 is True:
        report ( 'Please place the thermistors in a controlled temperature environment\nand wait for the temperature to stabilize at 0 C.\n\n ')
        cal_temp = input( 'Please enter exact calibration temperature 1: ')
        payload = get_cmd_payload()
        if not add_cal_temp_metric( payload, cal_temp, 1 ):
            return False
        byte_array = bytearray( payload.SerializeToString() )
        client.publish( NODE_CMD_TOPIC, byte_array, 0, False )
        report( f'Calibration temperature 1 is {cal_temp}', always = True )
        return True 
    elif temp2 is True:
        report ( 'Please place the thermistors in a controlled temperature environment \nand wait for the temperature to stabilize at 100 C.\n\n ')
        cal_temp = input( 'Please enter exact calibration temperature 2: ')
        payload = get_cmd_payload()
        if not add_cal_temp_metric( payload, cal_temp, 2 ):
            return False
        byte_array = bytearray( payload.SerializeToString() )
        client.publish( NODE_CMD_TOPIC, byte_array, 0, False )
        report( f'Calibration temperature 2 is {cal_temp}', always = True )
        return True 
    elif clear is True:
        confirm = input( 'Are you sure you want to permanently erase calibration data? (enter yes)')
        if (confirm  == 'yes'):
            send_simple_node_command("Node Control/Clear Cal Data", True)
        else:
            report ('Clear cal data has been aborted.')
    else:
        if send_simple_node_command( 'Node Control/Calibrated?', True ):
            report( 'Module calibration status requested', always = True )

def send_cal_gui_command(temp1, temp2, clear):

    if clear:
        send_simple_node_command("Node Control/Clear Cal Data", True)
    elif temp2 is None:
        payload = get_cmd_payload()
        if not add_cal_temp_metric( payload, temp1, 1 ):
            return False
        byte_array = bytearray( payload.SerializeToString() )
        client.publish( NODE_CMD_TOPIC, byte_array, 0, False )
        return True 
    elif temp1 is None:
        payload = get_cmd_payload()
        if not add_cal_temp_metric( payload, temp2, 2 ):
            return False
        byte_array = bytearray( payload.SerializeToString() )
        client.publish( NODE_CMD_TOPIC, byte_array, 0, False )
        return True 

# Add a metric to the payload to set the value on a TEC
def add_channel_metric( payload, channel_number, value ):
    if isinstance( channel_number, str ) and channel_number.lower() == 'all':
        # Special flag indicating all TECs
        for channel_number in range( 1, NUM_TEC + 1 ):
            if not add_channel_metric( payload, channel_number, value ):
                return False
        return True
    try:
        channel_number = int( channel_number )
    except ValueError:
        report( f'Invalid tec NUMBER, must be an integer or "all": "{channel_number}"', error = True, always = True )
        return False
    if channel_number <= 0 or channel_number > NUM_TEC:
        report( f'TEC NUMBER out of range 1 to {NUM_TEC}: {channel_number}', error = True, always = True )
        return False
    try:
        value = float( value )
    except ValueError: 
        return False
    if value < -100 or value > 100:
        report( f'Invalid tec VALUE, must be a number from -100 to 100: "{value}"', error = True, always = True )
        return False
    try:
        add_metric_as_alias( payload, None, f'Inputs/Power Channel{channel_number}', MetricDataType.Float, value )
    except ValueError:
        report( f'Unrecognized metric: "Inputs/Power Channel{channel_number}"', error = True, always = True )
        return False
    return True


# Ask the node to set the voltage on one or more TECs
def set_channel( channel_number, value ):
    payload = get_cmd_payload()
    if not add_channel_metric( payload, channel_number, value ):
        return False
    byte_array = bytearray( payload.SerializeToString() )
    client.publish( NODE_CMD_TOPIC, byte_array, 0, False )
    report( f'TEC {channel_number} set to {value}', always = True )
    return True
    
             
# Main program starts here

# Set the default option values
option_no_GUI = False
option_broker_URL = DEFAULT_BROKER_URL
option_broker_port = DEFAULT_BROKER_PORT
option_module_id = DEFAULT_MODULE_ID
option_do_reboot = False
option_show = 'changed'
option_do_exit = False
option_log = False
option_calibrate = False
option_do_set_channel = False
option_channel_number = 0
option_channel_value = 0.0
MIN_TEC_VALUE = -100
MAX_TEC_VALUE = 100
calibrated = False
calibrationINW = False

# Parse the command-line options
for arg in sys.argv[ 1: ]:
    lower_arg = arg.lower()
    if lower_arg == 'no_gui':
        option_no_GUI = True
    elif lower_arg.startswith( 'broker=' ):
        split_arg = arg.split( '=', 2 )
        if split_arg[ 1 ] != '':
            option_broker_URL = split_arg[ 1 ]
        if len( split_arg ) == 3:
            try:
                option_broker_port = int( split_arg[ 2 ] )
            except ValueError:
                report( f'Invalid BROKER_PORT: "{split_arg[ 2 ]}"', error = True, always = True )
                show_usage()
    elif lower_arg.startswith( 'module=' ):
        split_arg = arg.split( '=', 1 )
        option_module_id = split_arg[ 1 ]
    elif lower_arg == 'reboot':
        option_do_reboot = True
    elif lower_arg.startswith( 'tec=' ):
        if option_do_set_channel:
            report( 'Only one "tec" argument can be specified', error = True, always = True )
            show_usage()
        option_do_set_channel = True
        split_arg = arg.split( '=', 2 )
        if len( split_arg ) != 3:
            report( 'Invalid "tec" option, must be of the form "tec=NUMBER=VALUE"', error = True, always = True )
            show_usage()
        option_channel_number  = split_arg[ 1 ]
        option_channel_value = split_arg[ 2 ]
    elif lower_arg.startswith( 'show=' ):
        split_arg = arg.split( '=', 1 )
        option_show = split_arg[ 1 ].lower()
        if option_show not in SHOW_OPTIONS:
            report( f'Invalid "show" option, SHOW_WHAT must be one of {SHOW_OPTIONS}', error = True, always = True )
            show_usage()
    elif lower_arg == 'log':
        option_log = True
    elif lower_arg == 'exit':
        option_do_exit = True
    elif lower_arg == 'help' or lower_arg == '-help' or lower_arg == '--help' or lower_arg == 'h' or lower_arg == '-h':
        show_usage()
    else:
        report( f'Unrecognized command: "{arg}"', error = True, always = True )
        show_usage()

# Specify which module we're communicating with
if not change_module( option_module_id, None ):
    show_usage()

# Set up the MQTT client connection
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect( option_broker_URL, option_broker_port, 60 )
    report( f'Connecting to MQTT broker at {option_broker_URL}:{option_broker_port}', error = True, always = True )

except ConnectionRefusedError:
    report( f'Failed to connect to MQTT broker at {option_broker_URL}:{option_broker_port}', error = True, always = True )
    sys.exit()

close_thread = False
threading.Thread( target = client_loop ).start()

# Short delay to allow connect callback to occur
time.sleep( 0.5 )

# Issue any startup commands
if option_do_reboot:
    reboot_module()

if option_do_exit:
    # Quit after issuing command-line commands (if any)
    close_thread = True
    sys.exit()

def change_module_button_handler():
    module_id = change_module_input.text()
    if change_module( module_id, client ):
        main_window.setWindowTitle( f'TEC Client v{APP_VERSION} - Module {module_id}' )
        show_data_on_GUI()

def reboot_button_handler():
    reboot_module()

def data_button_handler():
    global option_data
    send_simple_node_command('Properties/Data Selection', option_data)
    if not option_data:
        report("Displaying Thermistor Temperature.")
    else:
        report("Displaying Seebeck Voltage.")

def log_button_handler():
    global option_log
    option_log = not option_log
    if option_log:
        report( 'Logging is on', always = True )
        log_button.setText( 'Toggle Logging Off' )
    else:
        report( 'Logging is off', always = True )
        log_button.setText( 'Toggle Logging On' )

def set_TEC_button_handler():
    set_channel( 'all', '0' )

def set_TEC_button_handler2():
    payload = get_cmd_payload()
    for channel in range(NUM_TEC):
        tec_widgets[channel].publish(payload)
        # Send the message
    byte_array = bytearray( payload.SerializeToString() )
    client.publish( NODE_CMD_TOPIC, byte_array, 0, False )

def cal_button_handler():
    global option_calibrate
    if not option_calibrate:
        report('Calibrate 1 INW')
        set_cal_label.setText('2) Place thermistors in a high reference temperature environement (100 C).')
        set_cal_button.setText('Calibrate High')
        send_cal_gui_command( set_cal_low_input.text(), None, False )
    else:
        report('Calibrate 2 INW')
        set_cal_label.setText('1) Place thermistors in a low reference temperature environement (0 C).')
        set_cal_button.setText('Calibrate Low')
        send_cal_gui_command( None, set_cal_low_input.text(), False )
    option_calibrate = not option_calibrate

def clear_cal_button_handler():
    send_cal_gui_command(None, None, True)

def set_labels():
    global status_label
    global calibration_label
    global thermistor_button
    global thermistor_label
    global option_data
    global calibrated 
    global calibrationINW

    status_label.setText(f'Calibrated?: {calibrated}')
    calibration_label.setText(f'Calibration in progress? : {calibrationINW}')

    if (option_data):
        thermistor_label.setText('Thermistor Temp (??C)')
        thermistor_button.setText( 'Display Seebeck Voltage' )
    else:
        thermistor_label.setText( 'Seebeck Voltage (mV)' )
        thermistor_button.setText( 'Display Thermistor Temp' )

# Select which UI to use
if option_no_GUI:
    # Run the interactive command-line UI
    print( f'Thermistor Mux Client v{APP_VERSION} connected to Module {option_module_id}' )
    while True:
        # Get the next command
        try:
            command = input( 'Enter command (? for help, Ctrl-D to quit): ' ).lower().split()
        except EOFError:
            # No more commands
            close_thread = True
            sys.exit()

        if len( command ) == 0:
            continue
        elif command[ 0 ] == 'module':
            if len( command ) != 2:
                report( 'Invalid use, must be of the form "module MODULE_ID"', error = True, always = True )
                continue
            if not change_module( command[ 1 ], client ):
                continue
        elif command[ 0 ] == 'reboot':
            reboot_module()
        elif command[ 0 ] == 'show':
            if len( command ) != 2:
                report( 'Invalid use, must be of the form "show SHOW_WHAT"', error = True, always = True )
                continue
            param = command[ 1 ].lower()
            if param not in SHOW_OPTIONS:
                report( f'Invalid use, SHOW_WHAT must be one of {SHOW_OPTIONS}', error = True, always = True )
                continue
            option_show = param
            report( f'Showing {option_show}', always = True )
        elif command[ 0 ] == 'log':
            option_log = not option_log
            if option_log:
                report( 'Logging is on', always = True )
            else:
                report( 'Logging is off', always = True )
        elif command[ 0 ] == 'quit' or command[ 0 ] == 'exit':
            close_thread = True
            sys.exit()
        elif command[ 0 ] == 'calibrate':
            if len( command ) != 2:
                report( 'Invalid use, must be of the form "calibrate CAL"', error = True, always = True )
                continue
            if command[ 1 ] not in CAL_OPTIONS:
                report( f'Invalid use, CAL must be one of {CAL_OPTIONS}', error = True, always = True )
                continue
            elif command [ 1 ] == 'temp1':
                send_cal_command(True, False, False)
            elif command [ 1 ] == 'temp2':
                send_cal_command(False, True, False)
            elif command [ 1 ] == 'clear':
                send_cal_command(False, False, True)
            else:
                metric = find_metric(None, 'Properties/Calibration Status')
                metric.value_str = f'{metric.value}'
                metric.timestamp_str = f'{metric.timestamp}'
                print( f'{metric.display_name} at {metric.timestamp_str} = {metric.value_str}' )
                metric = find_metric(None, 'Properties/Calibration INW')
                metric.value_str = f'{metric.value}'
                metric.timestamp_str = f'{metric.timestamp}'
                print( f'{metric.display_name} at {metric.timestamp_str} = {metric.value_str}' )
        elif command[ 0 ] == 'data':
            data_button_handler()
        elif command[ 0 ] == 'tec':
            if len( command ) != 3:
                report( 'Invalid use, must be of the form "tec NUMBER VALUE"', error = True, always = True )
                continue
            option_do_set_channel = True
            option_channel_number  = command[ 1 ]
            option_channel_value = command[ 2 ]
            set_channel(option_channel_number, option_channel_value)
        elif command[ 0 ] == 'help' or command[ 0 ] == 'h' or command[ 0 ] == '?':
            print( f'Thermistor Mux Client v{APP_VERSION} connected to Module {option_module_id}' )
            print( f'Commands:' )
            print( f'    module MODULE_ID = switch to the Thermistor Mux module number (0-{NUM_MODULES - 1})' )
            print( f'    reboot = send the Reboot command to the module' )
            print( f'    tec NUMBER VALUE = send the set TEC channel power command to the module:' )
            print( f'        NUMBER = which output to set (1-{NUM_TEC}, or "all" for all TECs)' )
            print( f'        VALUE = the floating-point power to set it to ({MIN_TEC_VALUE:.1f} to {MAX_TEC_VALUE:.1f}' )
            print( f'    show SHOW_WHAT = what to display on the command-line interface when a message is received, where SHOW_WHAT is one of:' )
            print( f'        none = don\'t display anything' )
            print( f'        errors = just display errors in incoming messages' )
            print( f'        topic = just display the message topic and errors' )
            print( f'        changed = display the message topic and only those metrics it contains' )
            print( f'        all = display the message topic and all the metrics from this module' )
            print( f'    calibrate CAL_OPTIONS = check calibration status, calibrate thermistors or clear calibration data, where CAL_OPTIONS is one of:')
            print( f'        temp1 = runs calibration routine for first temperature extreme. (Will set Calibration INW to true)')
            print( f'        temp2 = runs calibration routine for second temperature extreme.')
            print( f'        status = Displays thermistor mux calibration status.')
            print( f'        clear = Permanently deletes stored calibration data. (Temperature displayed will be then be raw values)')
            print( f'    log = toggle logging data messages to CSV on or off' )
            print( f'    data = toggle between displaying Seebeck voltage or Thermistor Temperature' )
            print( f'    quit, exit, <Ctrl-D> = stop this program' )
            print( f'    help, h, ? = display this list of commands' )
            print( f'Note: Only one command can be specified on the command-line.' )
        else:
            report( 'Unrecognized command', error = True, always = True )


from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

option_module_id = 0

def center_widget( widget ):
    h_box = QWidget()
    h_box_layout = QHBoxLayout()
    h_box.setLayout( h_box_layout )
    h_box_layout.addWidget( QLabel( '' ), 10 )
    h_box_layout.addWidget( widget, 0 )
    h_box_layout.addWidget( QLabel( '' ), 10 )
    return h_box

class Text_Metric:
    def __init__( self, grid, row, col, metric_name, can_set ):
        self.metric_name = metric_name
        self.current = QLabel( 'None' )
        grid.addWidget( self.current, row, col + 0, Qt.AlignCenter )
        if can_set:
            self.new = QLineEdit( '' )

            grid.addWidget( self.new, row, col + 1 )
        else:
            self.new = None

    # Clear the display of the current value
    def clear( self ):
        self.current.setText( '' )

    # Display the current value of the metric, if it matches
    def update( self, metric ):
        if self.metric_name == metric.name:
            self.current.setText( metric.value_str )
            return True
        else:
            return False

    # If a new value has been entered, add it to the list
    def add_for_set( self, name_list, value_list ):
        if self.new == None:
            return
        new_value = self.new.text()
        if new_value == '':
            # Nothing entered by user - don't add this metric
            return
        name_list.append( self.metric_name )
        value_list.append( new_value )

class Readonly_Checkbox( QCheckBox ):
    def __init__( self, text, parent = None ):
        super().__init__( text, parent )

    def nextCheckState( self ):
        return


class TEC_channel: 
    def __init__(self, tec_number, grid, row, col):
        self.tec_number = tec_number
        self.row_labels = []

        self.row_labels.append( None )
        self.label = QLabel( f'TEC{self.tec_number + 1 }' )
        grid.addWidget( self.label, row, col, 1, 2, Qt.AlignHCenter )

        self.metrics = []
        self.metrics.append( Text_Metric( grid, row, 2, f'Inputs/Power Channel{tec + 1}', True ) )

        self.metrics.append( Text_Metric( grid, row, 4, f'Outputs/Direction Channel{tec + 1}', False ) )

        self.metrics.append( Text_Metric( grid, row, 5, f'Outputs/Data Channel{tec + 1}', False ) )

        #self.metrics.append( Text_Metric( grid, row, 6, f'timestamp', False ) )

    def set_labels( self, grid, row, col ):
        for i in range( len( self.row_labels ) ):
            if self.row_labels[ i ] != None:
                grid.addWidget( QLabel( self.row_labels[ i ] + ":" ), row + i, col )

    def clear_all( self ):
        for metric in self.metrics:
            metric.clear()

    def show( self, metric_spec ):
        for metric in self.metrics:
            metric.update( metric_spec )

    def publish( self, payload ):
        name_list = []
        value_list = []
        for metric in self.metrics:
            metric.add_for_set( name_list, value_list )
        set_TEC( payload, self.tec_number, name_list, value_list )


def set_TEC( payload, tec_number, name_list, value_list ):
    if len( name_list ) == 0 or len( value_list ) == 0:
        report( f'No changes to send to module', error = True, always = True )
        return
    if len( name_list ) != len( value_list ):
        report( f'Mismatch between number of metric names ({len( name_list )}) and values ({len( value_list )})', error = True, always = True )
        return    
    try:
        #Construct the message
        #payload = get_cmd_payload()
        for i in range ( len( name_list ) ):
            metric_name = name_list[i]
            value       = value_list[i]
        value = get_pwr(value)

        # Add the metric to the payload
        try:
            add_metric_as_alias( payload, None, f'Inputs/Power Channel{tec_number + 1}',  MetricDataType.Float, value )
        except ValueError:
            report( f'Unrecognized metric: "{metric_name}"', error = True, always = True )
            return False

        # Send the message
        #byte_array = bytearray( payload.SerializeToString() )
        #client.publish( NODE_CMD_TOPIC, byte_array, 0, False )
    except ValueError:
        return False
    return True
            
def get_pwr(value):
    return get_float( value, 'Channel Power', MIN_TEC_VALUE, MAX_TEC_VALUE)

def get_float( value, name, min_valid, max_valid ):
    try:
        value = float( value )
    except ValueError:
        report( f'Invalid {name}, must be a number or "random": "{value}"', error = True, always = True )
        raise ValueError
    if value < min_valid or value > max_valid:
        report( f'{name} out of range {min_valid} to {max_valid}: {value}', error = True, always = True )
        raise ValueError
    return value

app = QApplication( [] )
main_window = QMainWindow()
main_window.setWindowTitle( f'Thermo_Electric Controller Client v{APP_VERSION} - Module {option_module_id}' )

window = QWidget()
v_box_layout = QVBoxLayout()
v_box_layout.setSpacing( 0 )
window.setLayout( v_box_layout )

main_window.setCentralWidget( window )

# Data received from the module
outputs = QWidget()
output_grid = QGridLayout()
outputs.setLayout( output_grid )

# The Change Module button
change_module_controls = QWidget()
h_box_layout = QHBoxLayout()
change_module_controls.setLayout( h_box_layout )
change_module_input = QLineEdit( f'{option_module_id}' )
only_int = QIntValidator()
change_module_input.setValidator( only_int )
h_box_layout.addWidget( change_module_input )
change_module_button = QPushButton( 'Change Module' )
change_module_button.clicked.connect( change_module_button_handler )
h_box_layout.addWidget( change_module_button )
v_box_layout.addWidget( center_widget( change_module_controls ) )

# The Reboot button
reboot_button = QPushButton( 'Reboot' )
reboot_button.clicked.connect( reboot_button_handler )
v_box_layout.addWidget( center_widget( reboot_button ) )

# The logging controls
log_button = QPushButton( '' )
log_button.clicked.connect( log_button_handler )
v_box_layout.addWidget( center_widget( log_button ) )

if option_log:
    log_button.setText( 'Toggle Logging Off' )
else:
    log_button.setText( 'Toggle Logging On' )

# The Seebeck/ Thermistor button
if (option_data):
    thermistor_button = QPushButton( 'Display Seebeck Voltage' )
else:
    thermistor_button = QPushButton( 'Display Thermistor Temp' )

thermistor_button.clicked.connect( data_button_handler )
v_box_layout.addWidget( center_widget(thermistor_button) )

# The TIC data and controls
tec_controls = QWidget()
tec_grid = QGridLayout()
tec_controls.setLayout( tec_grid )
v_box_layout.addWidget( tec_controls )

# Node data
tec_grid.addWidget( QLabel( 'TEC Channel' ), 0, 1 )
tec_grid.addWidget( QLabel( '   Current Power' ), 0, 2 )
tec_grid.addWidget( QLabel( '   New Power' ), 0, 3 )
tec_grid.addWidget( QLabel( 'Direction' ),   0, 4 )
thermistor_label = QLabel('Temp')
tec_grid.addWidget( thermistor_label, 0, 5 )
#tec_grid.addWidget( QLabel( 'Timestamp' ),   0, 6 )

tec_widgets = []
for tec in range( NUM_TEC ):
    tec_widgets.append( TEC_channel( tec, tec_grid, tec + 1, 0 ) )

# The row labels
tec_widgets[ 0 ].set_labels( tec_grid, 0, 0 )

# Set TEC button
set_TEC_button = QPushButton( 'Set TEC(s)' )
set_TEC_button.clicked.connect( set_TEC_button_handler2 )
tec_grid.addWidget( set_TEC_button,           13, 3 )

# All Off button
all_off_button = QPushButton( 'All Off' )
all_off_button.clicked.connect( set_TEC_button_handler )
tec_grid.addWidget( all_off_button,           13, 4 )

#v_box_layout.addWidget( center_widget( set_TEC_controls ) )

#Calibration Routine Layout
set_Calibration_label = QLabel( f'Calibration' )
v_box_layout.addWidget( center_widget( set_Calibration_label ) )

#Current Calibration Status
status_label = QLabel('')
calibration_label = QLabel('')
v_box_layout.addWidget( status_label, 0, Qt.AlignCenter )
v_box_layout.addWidget( calibration_label, 0, Qt.AlignCenter )

# Clear Calibration button
clear_cal_button = QPushButton( 'Clear Calibration' )
clear_cal_button.clicked.connect( clear_cal_button_handler )
v_box_layout.addWidget( clear_cal_button, 0, Qt.AlignCenter )

#Spacer
line_space = QLabel('')
v_box_layout.addWidget( center_widget( line_space ) )

# Calibration Routine 
set_cal_label = QLabel('1) Place thermistors in a low reference temperature environement (0 C).')
v_box_layout.addWidget( center_widget( set_cal_label ) )
set_cal_controls = QWidget()
set_cal_layout = QGridLayout()
set_cal_controls.setLayout( set_cal_layout )

# Calibration reference temp entry
set_cal_layout.addWidget( QLabel( 'Enter reference temperature:' ),   3, 0 )
set_cal_low_input = QLineEdit( '' )
set_cal_layout.addWidget( set_cal_low_input,     3, 1 )
set_cal_layout.addWidget( QLabel( f'degrees C' ), 3, 2 )

# Calibrate button
set_cal_button = QPushButton( 'Calibrate Low' )
set_cal_button.clicked.connect( cal_button_handler )
set_cal_layout.addWidget( set_cal_button,           3, 3 )
v_box_layout.addWidget( center_widget( set_cal_controls ) )

'''
# The diagnostic text view
diagnostic_text = QPlainTextEdit()
diagnostic_text.setReadOnly( True )
diagnostic_text.setMaximumBlockCount( 500 )
normal_format = diagnostic_text.currentCharFormat()
error_format = QTextCharFormat()
error_format.setForeground( Qt.red )
v_box_layout.addWidget( diagnostic_text )
'''
gui_controls_created = True

# Run the GUI
main_window.show()
exit_code = app.exec()
close_thread = True
sys.exit( exit_code )
