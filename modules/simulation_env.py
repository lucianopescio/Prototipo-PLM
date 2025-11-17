"""
Simulation environment helpers: wrappers for SimPy and OpenAI Gym.
"""
from typing import Any, Optional


def run_simpy_minimal(duration: float = 1.0, callback: Optional[Any] = None) -> dict:
    """Run a trivial SimPy timeout simulation and return timing info.
    If SimPy is not installed, raise ImportError.
    """
    try:
        import simpy
    except Exception:
        raise ImportError("SimPy is not installed. Install simpy to run simulations.")

    env = simpy.Environment()
    results = {"started": True, "duration": duration}

    def _proc(env, duration):
        yield env.timeout(duration)
        if callback:
            try:
                callback()
            except Exception:
                pass

    env.process(_proc(env, duration))
    env.run()
    return results


def make_gym_env(env_name: str = "CartPole-v1") -> Any:
    """Create and return a Gym environment. Raises ImportError if gym missing.
    Uses classic Gym API; for newer gymnasium changes may be needed.
    """
    try:
        import gym
    except Exception:
        raise ImportError("gym is not installed. Install gym to use make_gym_env.")

    return gym.make(env_name)
