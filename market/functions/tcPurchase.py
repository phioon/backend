

def is_D_pvpc_1001(closeA, close, pv72A, pv72, pv305A, pv305, pv1292):
    # 'tc_id':          'D_pvpc_1001',
    # 'tc_name':        'PV: Giant Above Price Setup',
    # 'tc_description': 'Price became greater than line pv72. '
    #                   'Line pv72 is greater than line pv305. '
    #                   'Line pv1292 is greater than Price. '

    if pv1292 is not None and \
            (closeA < pv72A or pv72A <= pv305A) and \
            pv1292 > close > pv72 >= pv305:
        return True
    return False


def is_D_pvpc_1002(closeA, close, pv72A, pv72, pv305A, pv305, pv1292):
    # 'tc_id':          'D_pvpc_1002',
    # 'tc_name':        'PV: Giant Bellow Price Setup',
    # 'tc_description': 'Price became greater than line pv72. '
    #                   'Line pv72 is greater than line pv305. '
    #                   'Line pv305 is greater than line pv1292. '

    if pv1292 is not None and \
            (closeA < pv72A or pv72A <= pv305A) and \
            close > pv72 >= pv305 > pv1292:
        return True
    return False


def is_D_pvpc_1003(closeA, close, pv72A, pv72, pv305A, pv305, pv610, pv1292):
    # 'tc_id':          'D_pvpc_1003',
    # 'tc_name':        'PV: Big Above Price Setup',
    # 'tc_description': 'Price became greater than line pv72. '
    #                   'Line pv72 is greater than pv305. '
    #                   'Line pv1292 doesn\'t exist. '
    #                   'Line pv610 is greater than Price.'

    if pv1292 is None and pv610 is not None and \
            (closeA < pv72A or pv72A <= pv305A) and \
            pv610 > close > pv72 >= pv305:
        return True
    return False


def is_D_pvpc_1004(closeA, close, pv72A, pv72, pv305A, pv305, pv610, pv1292):
    # 'tc_id' =         'D_pvpc_1004',
    # 'tc_name':        'PV: Big Bellow Price Setup',
    # 'tc_description': 'Price became greater than line pv72. '
    #                   'Line pv72 is greater than pv305. '
    #                   'Line pv1292 doesn\'t exist. '
    #                   'Line pv305 is greater than pv610.'

    if pv1292 is None and pv610 is not None and \
            (closeA < pv72A or pv72A <= pv305A) and \
            close > pv72 >= pv305 > pv610:
        return True
    return False
