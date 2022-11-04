from proof_data_analysis.replay import replay_from_file


class TestReplay:
    def test_replay(self):
        """Will open the replay window"""
        replay_from_file("tests/example.json")
