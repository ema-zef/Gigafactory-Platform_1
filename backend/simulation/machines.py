"""Equipment sizing with optional parent-web sizing for pre-slitting operations.

Pass ``geometry`` for coating/calendaring only, for example::

    geometry = {
        'collector_width_m': 0.061,
        'effective_parent_web_width_m': 0.700,
        'electrode_web_input_length_m_day': 1060505.4525,  # optional
    }
    calculate_machines(required_output_m_day, equipment, production, geometry=geometry)

``output_required`` is electrode-lane metres/day for pre-slitting steps.
Other steps, including vacuum drying, retain their existing units and behaviour.
Material purchasing/costing must separately consume the returned gross foil and
trim areas; this function does not change material requirements or costs.
"""
import math


def _optional_number(mapping, key):
    value = mapping.get(key)
    return float(value) if value is not None else None


def calculate_machines(output_required, equipment, production, geometry=None):
    hours_per_shift = float(production['hours_per_shift'])
    shifts = int(production['no_of_shifts_per_day'])
    available_hours_year = float(production['available_time_min'])  # legacy: hours/year
    if hours_per_shift <= 0 or shifts <= 0 or available_hours_year <= 0:
        raise ValueError('Shift hours, shifts/day, and available annual hours must be positive.')

    scheduled_hours_year = hours_per_shift * shifts * 365
    uptime = available_hours_year / scheduled_hours_year
    available_hours_day = available_hours_year / 365
    available_minutes_day = available_hours_day * 60

    technology_name = equipment.get('technology_name') or 'Unknown technology'
    category = (equipment.get('process_category') or '').strip().upper()
    process = (equipment.get('process') or '').strip().lower()
    speed = _optional_number(equipment, 'speed_m_min')
    processing_time = _optional_number(equipment, 'processingtime_min')
    capacity = _optional_number(equipment, 'capacity')
    required_output = float(output_required)
    if not math.isfinite(required_output) or required_output < 0:
        raise ValueError(f'Invalid output_required for {technology_name}: {output_required}')

    capacity_method = None
    batches = None
    width_details = {}
    sizing_output = required_output
    roll_category = category in ('ROLL', 'CATHODE_ROLL', 'ANODE_ROLL')
    # Width conversion applies only to operations before slitting. Vacuum drying
    # remains a cycle-based ROLL operation, never a width-multiplied operation.
    width_aware = roll_category and (
        'coating' in process or 'calender' in process or 'calendar' in process
    )
    if width_aware and speed is not None and speed > 0 and geometry is None:
        raise ValueError(f'{technology_name}: parent-web geometry is required for pre-slitting speed sizing.')
    if geometry is not None and width_aware:
        collector_width = _optional_number(geometry, 'collector_width_m')
        parent_width = _optional_number(geometry, 'effective_parent_web_width_m')
        machine_width = _optional_number(equipment, 'web_width')
        if any(v is None or not math.isfinite(v) or v <= 0
               for v in (collector_width, parent_width, machine_width)):
            raise ValueError(
                f'{technology_name}: collector_width_m, effective_parent_web_width_m '
                'and equipment.web_width must all be positive metres.'
            )
        if parent_width > machine_width + 1e-9:
            raise ValueError(
                f'{technology_name}: parent web width {parent_width:g} m exceeds '
                f'machine web width {machine_width:g} m.'
            )
        # Tiny epsilon protects against floating-point errors at exact multiples.
        lanes = math.floor(parent_width / collector_width + 1e-9)
        if lanes < 1:
            raise ValueError(
                f'{technology_name}: collector lane width {collector_width:g} m '
                f'exceeds parent web width {parent_width:g} m.'
            )
        usable_width = lanes * collector_width
        trim_width = max(0.0, parent_width - usable_width)
        sizing_output = required_output / lanes
        electrode_input_length = _optional_number(
            geometry, 'electrode_web_input_length_m_day'
        )
        if electrode_input_length is not None and (
            not math.isfinite(electrode_input_length) or electrode_input_length < 0
        ):
            raise ValueError('electrode_web_input_length_m_day must be nonnegative.')
        parent_input_length = (
            electrode_input_length / lanes if electrode_input_length is not None else None
        )
        width_details = {
            'machine_web_width_m': round(machine_width, 9),
            'collector_width_m': round(collector_width, 9),
            'effective_parent_web_width_m': round(parent_width, 9),
            'lanes_per_web': lanes,
            'usable_lane_width_m': round(usable_width, 9),
            'uncoated_trim_width_m': round(trim_width, 9),
            'electrode_web_length_m_day': round(required_output, 6),
            'parent_web_length_m_day': round(sizing_output, 6),
            'parent_web_input_length_m_day': (
                round(parent_input_length, 6) if parent_input_length is not None else None
            ),
            'gross_parent_foil_area_m2_day': (
                round(parent_input_length * parent_width, 6)
                if parent_input_length is not None else None
            ),
            'uncoated_trim_area_m2_day': (
                round(parent_input_length * trim_width, 6)
                if parent_input_length is not None else None
            ),
            'width_constraint': False,
        }

    if roll_category:
        if speed is not None and speed > 0:
            daily_capacity = speed * available_minutes_day
            capacity_method = 'speed_parent_web' if width_details else 'speed'
        elif capacity is not None and capacity > 0 and processing_time is not None and processing_time > 0:
            batches = math.floor(available_minutes_day / processing_time)
            if batches < 1:
                raise ValueError(
                    f'{technology_name} cannot complete one {processing_time:g}-min '
                    f'cycle in {available_minutes_day:g} available min/day.'
                )
            daily_capacity = batches * capacity
            capacity_method = 'roll_cycle'
        elif capacity is not None and capacity > 0:
            daily_capacity = capacity
            capacity_method = 'stored_capacity'
        else:
            raise ValueError(f'{technology_name} has insufficient ROLL capacity data.')
    else:
        if processing_time is not None and processing_time > 0 and capacity is not None and capacity > 0:
            daily_capacity = available_minutes_day * capacity / processing_time
            capacity_method = 'cycle'
        elif capacity is not None and capacity > 0:
            daily_capacity = capacity
            capacity_method = 'stored_capacity'
        else:
            raise ValueError(f'{technology_name} has insufficient capacity data.')
        if category in ('MASS', 'CATHODE_MASS', 'ANODE_MASS') and processing_time is not None and processing_time > 0:
            batches = math.ceil(available_minutes_day / processing_time)

    if not math.isfinite(daily_capacity) or daily_capacity <= 0:
        raise ValueError(f'Invalid daily capacity for {technology_name}: {daily_capacity}')
    result = {
        'machines': math.ceil(sizing_output / daily_capacity),
        'batches': batches,
        'shifts': shifts,
        'uptime': round(uptime, 6),
        'available_hours_year': round(available_hours_year, 6),
        'available_hours_day': round(available_hours_day, 6),
        'available_minutes_day': round(available_minutes_day, 6),
        'daily_capacity_per_machine': round(daily_capacity, 6),
        'capacity_method': capacity_method,
    }
    result.update(width_details)
    return result
