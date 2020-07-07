def is_D_pvpc_9001(closeA, close, pc72A, pc72, pc305A, pc305, pc1292):
    # 'tc_id':          'D_pvpc_9001',
    # 'tc_name':        'PC: Giant Bellow Price Setup',,
    # 'tc_description': 'Price became lower than line pc72. '
    #                   'Line pc72 is lower than line pc305.'
    #                   'Line pc1292 is lower than Price.'

    if pc1292 is not None and \
            (closeA > pc72A or pc72A >= pc305A) and \
            pc1292 < close < pc72 <= pc305:
        return True
    return False


def is_D_pvpc_9002(closeA, close, pc72A, pc72, pc305A, pc305, pc1292):
    # 'tc_id':          'D_pvpc_9002',
    # 'tc_name':        'PC: Giant Above Price Setup'
    # 'tc_description': 'Price became lower than line pc72. '
    #                   'Line pc72 is lower than line pc305. '
    #                   'Line pc305 is lower than line pc1292.'

    if pc1292 is not None and \
            (closeA > pc72A or pc72A >= pc305A) and \
            close < pc72 <= pc305 < pc1292:
        return True
    return False


def is_D_pvpc_9003(closeA, close, pc72A, pc72, pc305A, pc305, pc610, pc1292):
    # 'tc_id':          'D_pvpc_9003',
    # 'tc_name':        'PV: Big Bellow Price Setup',
    # 'tc_description': 'Price became lower than line pc72. '
    #                   'Line pc72 is lower than pc305. '
    #                   'Line pc1292 doesn't exist. '
    #                   'Line pc610 is lower than Price.'

    if pc1292 is None and pc610 is not None and \
            (closeA > pc72A or pc72A >= pc305A) and \
            pc610 < close < pc72 <= pc305:
        return True
    return False


def is_D_pvpc_9004(closeA, close, pc72A, pc72, pc305A, pc305, pc610, pc1292):
    # 'tc_id' =         'D_pvpc_9004',
    # 'tc_name':        'PV: Big Above Price Setup',
    # 'tc_description': 'Price became lower than line pc72. '
    #                   'Line pc72 is lower than pc305. '
    #                   'Line pc1292 doesn't exist. '
    #                   'Line pc610 is greater than Price.'

    if pc1292 is None and pc610 is not None and \
            (closeA > pc72A or pc72A >= pc305A) and \
            close < pc72 <= pc305 < pc610:
        return True
    return False
