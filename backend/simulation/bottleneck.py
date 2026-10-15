"""Identify the most capacity-constrained production operation."""


def identify_bottleneck(technologies):
    candidates = []

    for tech in technologies:
        if tech.get("execution_mode", "in_house") != "in_house":
            continue

        machine_info = tech.get("machines") or {}

        machine_count = float(
            machine_info.get("machines") or 0
        )

        daily_capacity = float(
            machine_info.get("daily_capacity_per_machine") or 0
        )

        required_output = float(
            tech.get("required_output") or 0
        )

        if required_output < 0:
            raise ValueError(
                f"Negative required output for {tech.get('process')}"
            )

        if required_output == 0:
            continue

        if machine_count <= 0 or daily_capacity <= 0:
            raise ValueError(
                f"Invalid machine count or daily capacity "
                f"for {tech.get('process')}"
            )

        utilization = required_output / (
            machine_count * daily_capacity
        )

        candidates.append((utilization, tech))

    return (
        max(candidates, key=lambda item: item[0])[1]
        if candidates
        else None
    )