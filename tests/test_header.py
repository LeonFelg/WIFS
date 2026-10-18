import protocol_header as h


def test_sensor_order_nicht_leer():
    assert len(h.SENSOR_ORDER) > 0
    assert all(len(e) == 3 for e in h.SENSOR_ORDER)
