# encoding:utf-8
import os
from enum import Enum

SG_SOFTWARE_PATH = os.path.join(os.path.abspath("."), "software")
SG_AUDIO_PATH = os.path.join(os.path.abspath("."), "media")
SG_DEVICE_FILE = os.path.join(SG_SOFTWARE_PATH, "devices.json")

ROLES = [
    'superuser',
    'customer',
    'org',
    'org_user'
]
USER_ROLE_CHOICES = [
    (0, 'superuser'),
    (1, 'customer'),
    (2, 'org'),
    (3, 'org_user')
]
CLOUD_MSG_TYPE_CHOICES = [
    (0, 'notice'),
    (1, 'upgrade'),
    (3, 'other')
]

PERMISSIONS = {
    'superuser': {'customer': ['customer_add', 'customer_edit', 'customer_delete', 'customer_view']},
    'customer': {
        'org': ['add_org', 'edit_org', 'delete_org'],
        'org_user': ['add_org_user', 'edit_org_user', 'delete_org_user'],
        'device': ['manage_device', 'add_device', 'view_device', 'edit_device', 'delete_device'],
    },
    'org': ['view_audio'],
    'org_user': ['view_audio'],

}
# 设备状态
DEVICE_STATUS_CHOICES = [
    (0, 'default'),
    (1, 'processing'),
    (2, 'recording'),
    (3, 'error')
]


class DeviceStatusEnum(Enum):
    DEFAULT = 0
    STOP = 0
    RUNNING = 1
    RECORDING = 2
    ERROR = 3


# FFT点数
FFT_POINT_CHOICES = [
    (64, '64'),
    (128, '128'),
    (256, '256')
]

# 音频输出通道
OUTPUT_CHANNEL_CHOICES = [
    (1, '单路输出'),
    (9, '9路输出:8MIC+1'),
    (17, '17路输出:16MIC+1')
]

# 编码器
AUDIO_ENCODER_CHOICES = [
    (1, 'PCM_S8'),
    (2, 'PCM_S16LE'),
    (3, 'PCM_S24LE'),
    (10, 'OPUS')
]

# 音频声道
AUDIO_CHANNELS_CHOICES = [
    (1, '单声道'),
    (2, '双声道')
]

# 音频采样率
AUDIO_SAMPLE_RATE_CHOICES = [
    (8000, '8000'),
    (12000, '12000'),
    (16000, '16000')
]
# 音频帧长（每帧采样数）
AUDIO_FRAME_SIZE_CHOICES = [
    (40, '40'),
    (50, '50'),
    (80, '80'),
    (160, '160'),
    (320, '320'),
    (640, '640')
]

# 音频编码器的比特率
AUDIO_BITRATE_CHOICES = [
    (16000, '16000'),
    (32000, '32000'),
    (48000, '48000')
]

SYSTEM_MSG_TYPE_CHOICES = [
    (1, '通知'),
    (2, '系统'),
]

USER_MANAGE_ROLES = [
    {
        'id': 'admin',
        'name': '管理员',
        'describe': '拥有所有权限',
        'status': 1,
        'creatorId': 'system',
        'createTime': 1497160610259,
        'deleted': 0,
        'permissions': [{
            'roleId': 'admin',
            'permissionId': 'comment',
            'permissionName': '评论管理',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"edit","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [
                {
                    'action': 'add',
                    'describe': '新增',
                    'defaultCheck': False
                },
                {
                    'action': 'query',
                    'describe': '查询',
                    'defaultCheck': False
                },
                {
                    'action': 'get',
                    'describe': '详情',
                    'defaultCheck': False
                },
                {
                    'action': 'edit',
                    'describe': '修改',
                    'defaultCheck': False
                },
                {
                    'action': 'delete',
                    'describe': '删除',
                    'defaultCheck': False
                }],
            'actionList': ['delete', 'edit'],
            'dataAccess': ''
        },
            {
                'roleId': 'admin',
                'permissionId': 'member',
                'permissionName': '会员管理',
                'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"edit","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
                'actionEntitySet': [{
                    'action': 'add',
                    'describe': '新增',
                    'defaultCheck': False
                },
                    {
                        'action': 'query',
                        'describe': '查询',
                        'defaultCheck': False
                    },
                    {
                        'action': 'get',
                        'describe': '详情',
                        'defaultCheck': False
                    },
                    {
                        'action': 'edit',
                        'describe': '修改',
                        'defaultCheck': False
                    },
                    {
                        'action': 'delete',
                        'describe': '删除',
                        'defaultCheck': False
                    }
                ],
                'actionList': ['query', 'get', 'edit', 'delete'],
                'dataAccess': False
            },
            {
                'roleId': 'admin',
                'permissionId': 'menu',
                'permissionName': '菜单管理',
                'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"import","defaultCheck":False,"describe":"导入"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"edit","defaultCheck":False,"describe":"修改"}]',
                'actionEntitySet': [{
                    'action': 'add',
                    'describe': '新增',
                    'defaultCheck': False
                },
                    {
                        'action': 'import',
                        'describe': '导入',
                        'defaultCheck': False
                    },
                    {
                        'action': 'get',
                        'describe': '详情',
                        'defaultCheck': False
                    },
                    {
                        'action': 'edit',
                        'describe': '修改',
                        'defaultCheck': False
                    }
                ],
                'actionList': ['add', 'import'],
                'dataAccess': ''
            },
            {
                'roleId': 'admin',
                'permissionId': 'role',
                'permissionName': '角色管理',
                'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"edit","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
                'actionEntitySet': [{
                    'action': 'add',
                    'describe': '新增',
                    'defaultCheck': False
                },
                    {
                        'action': 'get',
                        'describe': '详情',
                        'defaultCheck': False
                    },
                    {
                        'action': 'edit',
                        'describe': '修改',
                        'defaultCheck': False
                    },
                    {
                        'action': 'delete',
                        'describe': '删除',
                        'defaultCheck': False
                    }
                ],
                'actionList': '',
                'dataAccess': ''
            },
            {
                'roleId': 'admin',
                'permissionId': 'user',
                'permissionName': '用户管理',
                'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"import","defaultCheck":False,"describe":"导入"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"edit","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"},{"action":"export","defaultCheck":False,"describe":"导出"}]',
                'actionEntitySet': [{
                    'action': 'add',
                    'describe': '新增',
                    'defaultCheck': False
                },
                    {
                        'action': 'import',
                        'describe': '导入',
                        'defaultCheck': False
                    },
                    {
                        'action': 'get',
                        'describe': '详情',
                        'defaultCheck': False
                    },
                    {
                        'action': 'edit',
                        'describe': '修改',
                        'defaultCheck': False
                    },
                    {
                        'action': 'delete',
                        'describe': '删除',
                        'defaultCheck': False
                    },
                    {
                        'action': 'export',
                        'describe': '导出',
                        'defaultCheck': False
                    }
                ],
                'actionList': ['add', 'get'],
                'dataAccess': ''
            }
        ]
    },
    {
        'id': 'user',
        'name': '普通会员',
        'describe': '普通用户，只能查询',
        'status': 1,
        'creatorId': 'system',
        'createTime': 1497160610259,
        'deleted': 0,
        'permissions': [{
            'roleId': 'user',
            'permissionId': 'comment',
            'permissionName': '评论管理',
            'actions': '[{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"}]',
            'actionEntitySet': [{
                'action': 'query',
                'describe': '查询',
                'defaultCheck': False
            },
                {
                    'action': 'get',
                    'describe': '详情',
                    'defaultCheck': False
                }
            ],
            'actionList': ['query'],
            'dataAccess': ''
        },

            {
                'roleId': 'user',
                'permissionId': 'marketing',
                'permissionName': '营销管理',
                'actions': '[]',
                'actionEntitySet': [],
                'actionList': '',
                'dataAccess': ''
            },
            {
                'roleId': 'user',
                'permissionId': 'member',
                'permissionName': '会员管理',
                'actions': '[{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"}]',
                'actionEntitySet': [{
                    'action': 'query',
                    'describe': '查询',
                    'defaultCheck': False
                },
                    {
                        'action': 'get',
                        'describe': '详情',
                        'defaultCheck': False
                    }
                ],
                'actionList': '',
                'dataAccess': ''
            },
            {
                'roleId': 'user',
                'permissionId': 'menu',
                'permissionName': '菜单管理',
                'actions': '[]',
                'actionEntitySet': [],
                'actionList': '',
                'dataAccess': ''
            },

            {
                'roleId': 'user',
                'permissionId': 'order',
                'permissionName': '订单管理',
                'actions': '[{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"}]',
                'actionEntitySet': [{
                    'action': 'query',
                    'describe': '查询',
                    'defaultCheck': False
                },
                    {
                        'action': 'get',
                        'describe': '详情',
                        'defaultCheck': False
                    }
                ],
                'actionList': '',
                'dataAccess': ''
            },
            {
                'roleId': 'user',
                'permissionId': 'permission',
                'permissionName': '权限管理',
                'actions': '[]',
                'actionEntitySet': [],
                'actionList': '',
                'dataAccess': ''
            },
            {
                'roleId': 'user',
                'permissionId': 'role',
                'permissionName': '角色管理',
                'actions': '[]',
                'actionEntitySet': [],
                'actionList': '',
                'dataAccess': ''
            },

            {
                'roleId': 'user',
                'permissionId': 'test',
                'permissionName': '测试权限',
                'actions': '[]',
                'actionEntitySet': [],
                'actionList': '',
                'dataAccess': ''
            },
            {
                'roleId': 'user',
                'permissionId': 'user',
                'permissionName': '用户管理',
                'actions': '[]',
                'actionEntitySet': [],
                'actionList': '',
                'dataAccess': ''
            }
        ]
    }
]
USER_MANAGE_PERMISSIONS = []

USER_MENU_ROLES = {
    'id': 'admin',
    'name': '管理员',
    'describe': '拥有所有权限',
    'status': 1,
    'creatorId': 'system',
    'createTime': 1497160610259,
    'deleted': 0,
    'permissions': [
        {
            'roleId': 'admin',
            'permissionId': 'dashboard',
            'permissionName': '仪表盘',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'query',
                'describe': '查询',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'device',
            'permissionName': '设备管理',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'audio',
            'permissionName': '音频管理',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'exception',
            'permissionName': '异常页面权限',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'query',
                'describe': '查询',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'result',
            'permissionName': '结果权限',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'query',
                'describe': '查询',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'profile',
            'permissionName': '详细页权限',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'query',
                'describe': '查询',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'table',
            'permissionName': '表格权限',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"import","defaultCheck":False,"describe":"导入"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'import',
                'describe': '导入',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'form',
            'permissionName': '表单权限',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'query',
                'describe': '查询',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'permission',
            'permissionName': '权限管理',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'role',
            'permissionName': '角色管理',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'table',
            'permissionName': '桌子管理',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'query',
                'describe': '查询',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },
        {
            'roleId': 'admin',
            'permissionId': 'user',
            'permissionName': '用户管理',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"import","defaultCheck":False,"describe":"导入"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"},{"action":"export","defaultCheck":False,"describe":"导出"}]',
            'actionEntitySet': [{
                'action': 'add',
                'describe': '新增',
                'defaultCheck': False
            }, {
                'action': 'import',
                'describe': '导入',
                'defaultCheck': False
            }, {
                'action': 'get',
                'describe': '详情',
                'defaultCheck': False
            }, {
                'action': 'update',
                'describe': '修改',
                'defaultCheck': False
            }, {
                'action': 'delete',
                'describe': '删除',
                'defaultCheck': False
            }, {
                'action': 'export',
                'describe': '导出',
                'defaultCheck': False
            }],
            'actionList': '',
            'dataAccess': ''
        },

    ]
}
DASHBOARD_MENU_PERMISSIONS = {
    'roleId': 'admin',
    'permissionId': 'dashboard',
    'permissionName': '仪表盘',
    'actions': '[]',
    'actionEntitySet': [],
    'actionList': '',
    'dataAccess': ''
}

USER_MENU_PERMISSIONS = {
    'roleId': 'admin',
    'permissionId': 'support',
    'permissionName': '超级模块',
    'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"import","defaultCheck":False,"describe":"导入"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"},{"action":"export","defaultCheck":False,"describe":"导出"}]',
    'actionEntitySet': [{
        'action': 'add',
        'describe': '新增',
        'defaultCheck': False
    }, {
        'action': 'import',
        'describe': '导入',
        'defaultCheck': False
    }, {
        'action': 'get',
        'describe': '详情',
        'defaultCheck': False
    }, {
        'action': 'update',
        'describe': '修改',
        'defaultCheck': False
    }, {
        'action': 'delete',
        'describe': '删除',
        'defaultCheck': False
    }, {
        'action': 'export',
        'describe': '导出',
        'defaultCheck': False
    }],
    'actionList': '',
    'dataAccess': ''
}
