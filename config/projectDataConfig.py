# -*- coding:utf-8 -*-

project_default_conf = {
    "table": "prod_clean_v3",
    "count_condi": "lop!=''",
    "schema": [
        "Index", "Id", "Hospname", "Province", "City", "lHospname", "lHospalias", "lDistrict", "lAddress", "lLevel", "lCat",
        "lTel", "lOffweb", "lStatus", "lop", "ltm", "cst", "cop", "ctm"
    ],
    "trans_schema": [
        "序号", "Id", "医院名称", "省", "市", "医院现用名称", "医院别名/曾用名", "所属区县", "医院地址", "医院等级", "经济类型",
        "医院电话", "医院网址", "经营状态", "操作员", "操作时间", "质检结果", "质检员", "质检时间"
    ],
    "condi_schema": [
        "uid", "uname", "condi"
    ],
    "condi_schema_local": [
        "uid", "uname", "condi", "min", "max"
    ],
    "can_change_cols": [
        "医院现用名称", "医院别名/曾用名", "所属区县", "医院地址", "医院等级", "经济类型", "医院电话", "医院网址", "经营状态"
    ],
    "non_null_cols": [
        "医院网址"
    ],
    "qc_can_change_cols": [
        "医院现用名称", "医院别名/曾用名", "所属区县", "医院地址", "医院等级", "经济类型", "医院电话", "医院网址", "经营状态", "质检结果"
    ],
    "qc_non_null_cols": [
        "医院网址"
    ]
}
