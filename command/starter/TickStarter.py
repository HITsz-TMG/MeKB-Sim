import subprocess
from command.command_base import CommandBase

class TickStarter(CommandBase):
    """start tick."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid']):
            return False
        
        tick_state = self.app.tick_state
        if tick_state["start"]:
            # return self.error("already start")
            pass
        elif self.app.get_nowtime() - tick_state["start_time"] < self.app.config.tick_cooldown:
            return self.error("still cooldown")
        # cmd = f"nohup python3.9 -u tick.py {self.app.config.tick_count_limit} >> logs/tick.log 2>&1 &"
        cmd = f"python tick.py"
        # cmd = "py -3.9 tick.py"
        # subprocess.getstatusoutput(cmd)
        subprocess.Popen(["python", "tick.py"])
        self.app.tick_state = {
            "start_time": self.app.get_nowtime(),
            "tick_count": 0,
            "start": True,
        }
        # Return nonce and sign message.
        return {'start': True}
