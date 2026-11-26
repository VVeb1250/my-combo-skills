from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    movement: str
    fire: bool


def decide(order: str, risk: int, smoke: bool, loaded: bool) -> Action:
    if order == "hold":
        return Action("hold", loaded)
    if order == "move":
        return Action("advance", loaded)
    if order != "free":
        raise ValueError("unknown order")
    if risk >= 70:
        return Action("retreat", False)
    return Action("hold", loaded)
