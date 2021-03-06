/********************************************************************************
 * Copyright (c) 2014-2019 Cirrus Link Solutions and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * Contributors:
 *   Cirrus Link Solutions - initial implementation
 ********************************************************************************/

/* Automatically generated nanopb header */
/* Generated by nanopb-0.3.5 at Sun Jun  2 14:12:25 2019. */

#ifndef PB_TAHU_PB_H_INCLUDED
#define PB_TAHU_PB_H_INCLUDED
#include "pb.h"

/* @@protoc_insertion_point(includes) */
#if PB_PROTO_HEADER_VERSION != 30
#error Regenerate this file with the current version of nanopb generator.
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Struct definitions */
typedef struct _org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_DataSetValueExtension {
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_DataSetValueExtension) */
} org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_DataSetValueExtension;

typedef struct _org_eclipse_tahu_protobuf_Payload_DataSet_Row {
    pb_size_t elements_count;
    struct _org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue *elements;
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_DataSet_Row) */
} org_eclipse_tahu_protobuf_Payload_DataSet_Row;

typedef struct _org_eclipse_tahu_protobuf_Payload_Metric_MetricValueExtension {
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_Metric_MetricValueExtension) */
} org_eclipse_tahu_protobuf_Payload_Metric_MetricValueExtension;

typedef struct _org_eclipse_tahu_protobuf_Payload_PropertySet {
    pb_size_t keys_count;
    char **keys;
    pb_size_t values_count;
    struct _org_eclipse_tahu_protobuf_Payload_PropertyValue *values;
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_PropertySet) */
} org_eclipse_tahu_protobuf_Payload_PropertySet;

typedef struct _org_eclipse_tahu_protobuf_Payload_PropertySetList {
    pb_size_t propertyset_count;
    struct _org_eclipse_tahu_protobuf_Payload_PropertySet *propertyset;
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_PropertySetList) */
} org_eclipse_tahu_protobuf_Payload_PropertySetList;

typedef struct _org_eclipse_tahu_protobuf_Payload_PropertyValue_PropertyValueExtension {
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_PropertyValue_PropertyValueExtension) */
} org_eclipse_tahu_protobuf_Payload_PropertyValue_PropertyValueExtension;

typedef struct _org_eclipse_tahu_protobuf_Payload_Template_Parameter_ParameterValueExtension {
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_Template_Parameter_ParameterValueExtension) */
} org_eclipse_tahu_protobuf_Payload_Template_Parameter_ParameterValueExtension;

typedef struct _org_eclipse_tahu_protobuf_Payload {
    bool has_timestamp;
    uint64_t timestamp;
    pb_size_t metrics_count;
    struct _org_eclipse_tahu_protobuf_Payload_Metric *metrics;
    bool has_seq;
    uint64_t seq;
    char *uuid;
    pb_bytes_array_t *body;
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload) */
} org_eclipse_tahu_protobuf_Payload;

typedef struct _org_eclipse_tahu_protobuf_Payload_DataSet {
    bool has_num_of_columns;
    uint64_t num_of_columns;
    pb_size_t columns_count;
    char **columns;
    pb_size_t types_count;
    uint32_t *types;
    pb_size_t rows_count;
    struct _org_eclipse_tahu_protobuf_Payload_DataSet_Row *rows;
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_DataSet) */
} org_eclipse_tahu_protobuf_Payload_DataSet;

typedef struct _org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue {
    pb_size_t which_value;
    union {
        uint32_t int_value;
        uint64_t long_value;
        float float_value;
        double double_value;
        bool boolean_value;
        char *string_value;
        org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_DataSetValueExtension extension_value;
    } value;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue) */
} org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue;

typedef struct _org_eclipse_tahu_protobuf_Payload_MetaData {
    bool has_is_multi_part;
    bool is_multi_part;
    char *content_type;
    bool has_size;
    uint64_t size;
    bool has_seq;
    uint64_t seq;
    char *file_name;
    char *file_type;
    char *md5;
    char *description;
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_MetaData) */
} org_eclipse_tahu_protobuf_Payload_MetaData;

typedef struct _org_eclipse_tahu_protobuf_Payload_PropertyValue {
    bool has_type;
    uint32_t type;
    bool has_is_null;
    bool is_null;
    pb_size_t which_value;
    union {
        uint32_t int_value;
        uint64_t long_value;
        float float_value;
        double double_value;
        bool boolean_value;
        char *string_value;
        org_eclipse_tahu_protobuf_Payload_PropertySet propertyset_value;
        org_eclipse_tahu_protobuf_Payload_PropertySetList propertysets_value;
        org_eclipse_tahu_protobuf_Payload_PropertyValue_PropertyValueExtension extension_value;
    } value;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_PropertyValue) */
} org_eclipse_tahu_protobuf_Payload_PropertyValue;

typedef struct _org_eclipse_tahu_protobuf_Payload_Template {
    char *version;
    pb_size_t metrics_count;
    struct _org_eclipse_tahu_protobuf_Payload_Metric *metrics;
    pb_size_t parameters_count;
    struct _org_eclipse_tahu_protobuf_Payload_Template_Parameter *parameters;
    char *template_ref;
    bool has_is_definition;
    bool is_definition;
    pb_extension_t *extensions;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_Template) */
} org_eclipse_tahu_protobuf_Payload_Template;

typedef struct _org_eclipse_tahu_protobuf_Payload_Template_Parameter {
    char *name;
    bool has_type;
    uint32_t type;
    pb_size_t which_value;
    union {
        uint32_t int_value;
        uint64_t long_value;
        float float_value;
        double double_value;
        bool boolean_value;
        char *string_value;
        org_eclipse_tahu_protobuf_Payload_Template_Parameter_ParameterValueExtension extension_value;
    } value;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_Template_Parameter) */
} org_eclipse_tahu_protobuf_Payload_Template_Parameter;

typedef struct _org_eclipse_tahu_protobuf_Payload_Metric {
    char *name;
    bool has_alias;
    uint64_t alias;
    bool has_timestamp;
    uint64_t timestamp;
    bool has_datatype;
    uint32_t datatype;
    bool has_is_historical;
    bool is_historical;
    bool has_is_transient;
    bool is_transient;
    bool has_is_null;
    bool is_null;
    bool has_metadata;
    org_eclipse_tahu_protobuf_Payload_MetaData metadata;
    bool has_properties;
    org_eclipse_tahu_protobuf_Payload_PropertySet properties;
    pb_size_t which_value;
    union {
        uint32_t int_value;
        uint64_t long_value;
        float float_value;
        double double_value;
        bool boolean_value;
        char *string_value;
        pb_bytes_array_t *bytes_value;
        org_eclipse_tahu_protobuf_Payload_DataSet dataset_value;
        org_eclipse_tahu_protobuf_Payload_Template template_value;
        org_eclipse_tahu_protobuf_Payload_Metric_MetricValueExtension extension_value;
    } value;
/* @@protoc_insertion_point(struct:org_eclipse_tahu_protobuf_Payload_Metric) */
} org_eclipse_tahu_protobuf_Payload_Metric;

/* Default values for struct fields */

/* Initializer values for message structs */
#define org_eclipse_tahu_protobuf_Payload_init_default {false, 0, 0, NULL, false, 0, NULL, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_Template_init_default {NULL, 0, NULL, 0, NULL, NULL, false, 0, NULL}
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_init_default {NULL, false, 0, 0, {0}}
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_ParameterValueExtension_init_default {NULL}
#define org_eclipse_tahu_protobuf_Payload_DataSet_init_default {false, 0, 0, NULL, 0, NULL, 0, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_init_default {0, {0}}
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_DataSetValueExtension_init_default {NULL}
#define org_eclipse_tahu_protobuf_Payload_DataSet_Row_init_default {0, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_init_default {false, 0, false, 0, 0, {0}}
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_PropertyValueExtension_init_default {NULL}
#define org_eclipse_tahu_protobuf_Payload_PropertySet_init_default {0, NULL, 0, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_PropertySetList_init_default {0, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_MetaData_init_default {false, 0, NULL, false, 0, false, 0, NULL, NULL, NULL, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_Metric_init_default {NULL, false, 0, false, 0, false, 0, false, 0, false, 0, false, 0, false, org_eclipse_tahu_protobuf_Payload_MetaData_init_default, false, org_eclipse_tahu_protobuf_Payload_PropertySet_init_default, 0, {0}}
#define org_eclipse_tahu_protobuf_Payload_Metric_MetricValueExtension_init_default {NULL}
#define org_eclipse_tahu_protobuf_Payload_init_zero {false, 0, 0, NULL, false, 0, NULL, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_Template_init_zero {NULL, 0, NULL, 0, NULL, NULL, false, 0, NULL}
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_init_zero {NULL, false, 0, 0, {0}}
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_ParameterValueExtension_init_zero {NULL}
#define org_eclipse_tahu_protobuf_Payload_DataSet_init_zero {false, 0, 0, NULL, 0, NULL, 0, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_init_zero {0, {0}}
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_DataSetValueExtension_init_zero {NULL}
#define org_eclipse_tahu_protobuf_Payload_DataSet_Row_init_zero {0, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_init_zero {false, 0, false, 0, 0, {0}}
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_PropertyValueExtension_init_zero {NULL}
#define org_eclipse_tahu_protobuf_Payload_PropertySet_init_zero {0, NULL, 0, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_PropertySetList_init_zero {0, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_MetaData_init_zero {false, 0, NULL, false, 0, false, 0, NULL, NULL, NULL, NULL, NULL}
#define org_eclipse_tahu_protobuf_Payload_Metric_init_zero {NULL, false, 0, false, 0, false, 0, false, 0, false, 0, false, 0, false, org_eclipse_tahu_protobuf_Payload_MetaData_init_zero, false, org_eclipse_tahu_protobuf_Payload_PropertySet_init_zero, 0, {0}}
#define org_eclipse_tahu_protobuf_Payload_Metric_MetricValueExtension_init_zero {NULL}

/* Field tags (for use in manual encoding/decoding) */
#define org_eclipse_tahu_protobuf_Payload_DataSet_Row_elements_tag 1
#define org_eclipse_tahu_protobuf_Payload_PropertySet_keys_tag 1
#define org_eclipse_tahu_protobuf_Payload_PropertySet_values_tag 2
#define org_eclipse_tahu_protobuf_Payload_PropertySetList_propertyset_tag 1
#define org_eclipse_tahu_protobuf_Payload_timestamp_tag 1
#define org_eclipse_tahu_protobuf_Payload_metrics_tag 2
#define org_eclipse_tahu_protobuf_Payload_seq_tag 3
#define org_eclipse_tahu_protobuf_Payload_uuid_tag 4
#define org_eclipse_tahu_protobuf_Payload_body_tag 5
#define org_eclipse_tahu_protobuf_Payload_DataSet_num_of_columns_tag 1
#define org_eclipse_tahu_protobuf_Payload_DataSet_columns_tag 2
#define org_eclipse_tahu_protobuf_Payload_DataSet_types_tag 3
#define org_eclipse_tahu_protobuf_Payload_DataSet_rows_tag 4
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_int_value_tag 1
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_long_value_tag 2
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_float_value_tag 3
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_double_value_tag 4
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_boolean_value_tag 5
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_string_value_tag 6
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_extension_value_tag 7
#define org_eclipse_tahu_protobuf_Payload_MetaData_is_multi_part_tag 1
#define org_eclipse_tahu_protobuf_Payload_MetaData_content_type_tag 2
#define org_eclipse_tahu_protobuf_Payload_MetaData_size_tag 3
#define org_eclipse_tahu_protobuf_Payload_MetaData_seq_tag 4
#define org_eclipse_tahu_protobuf_Payload_MetaData_file_name_tag 5
#define org_eclipse_tahu_protobuf_Payload_MetaData_file_type_tag 6
#define org_eclipse_tahu_protobuf_Payload_MetaData_md5_tag 7
#define org_eclipse_tahu_protobuf_Payload_MetaData_description_tag 8
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_int_value_tag 3
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_long_value_tag 4
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_float_value_tag 5
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_double_value_tag 6
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_boolean_value_tag 7
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_string_value_tag 8
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_propertyset_value_tag 9
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_propertysets_value_tag 10
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_extension_value_tag 11
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_type_tag 1
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_is_null_tag 2
#define org_eclipse_tahu_protobuf_Payload_Template_version_tag 1
#define org_eclipse_tahu_protobuf_Payload_Template_metrics_tag 2
#define org_eclipse_tahu_protobuf_Payload_Template_parameters_tag 3
#define org_eclipse_tahu_protobuf_Payload_Template_template_ref_tag 4
#define org_eclipse_tahu_protobuf_Payload_Template_is_definition_tag 5
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_int_value_tag 3
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_long_value_tag 4
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_float_value_tag 5
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_double_value_tag 6
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_boolean_value_tag 7
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_string_value_tag 8
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_extension_value_tag 9
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_name_tag 1
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_type_tag 2
#define org_eclipse_tahu_protobuf_Payload_Metric_int_value_tag 10
#define org_eclipse_tahu_protobuf_Payload_Metric_long_value_tag 11
#define org_eclipse_tahu_protobuf_Payload_Metric_float_value_tag 12
#define org_eclipse_tahu_protobuf_Payload_Metric_double_value_tag 13
#define org_eclipse_tahu_protobuf_Payload_Metric_boolean_value_tag 14
#define org_eclipse_tahu_protobuf_Payload_Metric_string_value_tag 15
#define org_eclipse_tahu_protobuf_Payload_Metric_bytes_value_tag 16
#define org_eclipse_tahu_protobuf_Payload_Metric_dataset_value_tag 17
#define org_eclipse_tahu_protobuf_Payload_Metric_template_value_tag 18
#define org_eclipse_tahu_protobuf_Payload_Metric_extension_value_tag 19
#define org_eclipse_tahu_protobuf_Payload_Metric_name_tag 1
#define org_eclipse_tahu_protobuf_Payload_Metric_alias_tag 2
#define org_eclipse_tahu_protobuf_Payload_Metric_timestamp_tag 3
#define org_eclipse_tahu_protobuf_Payload_Metric_datatype_tag 4
#define org_eclipse_tahu_protobuf_Payload_Metric_is_historical_tag 5
#define org_eclipse_tahu_protobuf_Payload_Metric_is_transient_tag 6
#define org_eclipse_tahu_protobuf_Payload_Metric_is_null_tag 7
#define org_eclipse_tahu_protobuf_Payload_Metric_metadata_tag 8
#define org_eclipse_tahu_protobuf_Payload_Metric_properties_tag 9

/* Struct field encoding specification for nanopb */
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_fields[7];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_Template_fields[7];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_Template_Parameter_fields[10];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_Template_Parameter_ParameterValueExtension_fields[2];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_DataSet_fields[6];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_fields[8];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_DataSetValueExtension_fields[2];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_DataSet_Row_fields[3];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_PropertyValue_fields[12];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_PropertyValue_PropertyValueExtension_fields[2];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_PropertySet_fields[4];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_PropertySetList_fields[3];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_MetaData_fields[10];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_Metric_fields[20];
extern const pb_field_t org_eclipse_tahu_protobuf_Payload_Metric_MetricValueExtension_fields[2];

/* Maximum encoded size of messages (where known) */
#define org_eclipse_tahu_protobuf_Payload_Template_Parameter_ParameterValueExtension_size 0
#define org_eclipse_tahu_protobuf_Payload_DataSet_DataSetValue_DataSetValueExtension_size 0
#define org_eclipse_tahu_protobuf_Payload_PropertyValue_PropertyValueExtension_size 0
#define org_eclipse_tahu_protobuf_Payload_Metric_MetricValueExtension_size 0

/* Message IDs (where set with "msgid" option) */
#ifdef PB_MSGID

#define TAHU_MESSAGES \


#endif

#ifdef __cplusplus
} /* extern "C" */
#endif
/* @@protoc_insertion_point(eof) */

#endif
