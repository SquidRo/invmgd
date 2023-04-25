#
# util_dflt.py
#
# Utility APIs for default inventory parameters
#

# ex: (name, weight, reserved_stack)
DFLT_INV_DATA = [
    ("K2V4PCB",   9, 6),
    ("TPM",       8, 2),
    ("IRON",      7, 3),
    ("CAGE",      6, 4),
    ("HEAT_SINK", 5, 6),
    ("AIR_BAFFLE",4, 3),
    ("BRACKET",   3, 3)
]

# number per box
DFLT_NPB_PCB      = 180
DFLT_NPB_TPM      = 4095
DFLT_NPB_IRON     = 1800
DFLT_NPB_CAGE     = 336
DFLT_NPB_HEAT_SINK= 234
DFLT_NPB_AIR_B    = 780
DFLT_NPB_BRACKET  = 1144

# ex: (quan)
DFLT_INV_BOX_DATA = [
    (DFLT_NPB_PCB,),
    (DFLT_NPB_TPM,),
    (DFLT_NPB_IRON,),
    (DFLT_NPB_CAGE,),
    (DFLT_NPB_HEAT_SINK,),
    (DFLT_NPB_AIR_B,),
    (DFLT_NPB_BRACKET,)
]

DFLT_NUM_PCB      = 180
DFLT_NUM_TPM      = 4095
DFLT_NUM_IRON     = 1800
DFLT_NUM_CAGE     = 336
DFLT_NUM_HEAT_SINK= 234
DFLT_NUM_AIR_B    = 780
DFLT_NUM_BRACKET  = 1144

# ex: (inv_id, quan, stk_id, ready)
DFLT_STO_DATA = [
    (1, DFLT_NUM_PCB, 1, 1),
    (1, DFLT_NUM_PCB, 2, 1),
    (1, DFLT_NUM_PCB, 3, 1),
    (1, DFLT_NUM_PCB, 4, 1),
    (1, DFLT_NUM_PCB, 5, 1),
    (1, DFLT_NUM_PCB, 6, 1),
    (2, DFLT_NUM_TPM, 7, 1),
    (2, DFLT_NUM_TPM, 8, 1),
    (3, DFLT_NUM_IRON, 9, 1),
    (3, DFLT_NUM_IRON, 10, 1),
    (3, DFLT_NUM_IRON, 11, 1),
    (4, DFLT_NUM_CAGE, 12, 1),
    (4, DFLT_NUM_CAGE, 13, 1),
    (4, DFLT_NUM_CAGE, 14, 1),
    (4, DFLT_NUM_CAGE, 15, 1),
    (5, DFLT_NUM_HEAT_SINK, 16, 1),
    (5, DFLT_NUM_HEAT_SINK, 17, 1),
    (5, DFLT_NUM_HEAT_SINK, 18, 1),
    (5, DFLT_NUM_HEAT_SINK, 19, 1),
    (5, DFLT_NUM_HEAT_SINK, 20, 1),
    (5, DFLT_NUM_HEAT_SINK, 21, 1),
    (6, DFLT_NUM_AIR_B, 22, 1),
    (6, DFLT_NUM_AIR_B, 23, 1),
    (6, DFLT_NUM_AIR_B, 24, 1),
    (7, DFLT_NUM_BRACKET, 25, 1),
    (7, DFLT_NUM_BRACKET, 26, 1),
    (7, DFLT_NUM_BRACKET, 27, 1),
    (None, None, None, None),
    (None, None, None, None),
    (None, None, None, None),
]

