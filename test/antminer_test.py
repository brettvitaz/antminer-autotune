from unittest.mock import Mock, PropertyMock, patch

import inspect

from antminer_autotune.antminer import Antminer
from antminer_autotune.models import models


class TestAntminer:
    def test_antminer_args(self):
        device = Antminer('127.0.0.1', 's7')

        assert(device.model == models['s7'])

    def test_antminer_freq(self):
        print(inspect.getmodule(Antminer))
        with patch('antminer_autotune.antminer.Antminer.api_frequency', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = 700
            device = Antminer('127.0.0.1', 's7')

            assert(device.model == models['s7'])
            assert(device.api_frequency == 700)
            assert(device.next_frequency() == 700)
            assert(device.prev_frequency() == 693)
