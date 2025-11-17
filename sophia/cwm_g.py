"""
CWM-G - Continuous World Model (Grounded)

The Grounded World Model maintains grounded physical/sensor state representation
of the world. It processes sensor data from Talos and maintains low-level
physical state information.

This component bridges the gap between abstract reasoning (CWM-A) and
physical reality (sensor/actuator data).

Reference: Section 3.3, Phase 2 (Section 7.2)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SensorType(Enum):
    """Types of sensors supported by CWM-G"""
    CAMERA = "camera"
    DEPTH = "depth"
    IMU = "imu"
    FORCE = "force"
    POSITION = "position"


@dataclass
class SensorReading:
    """Represents a sensor reading"""
    sensor_type: SensorType
    timestamp: float
    data: dict[str, Any]
    confidence: float = 1.0


class CWMGrounded:
    """
    Continuous World Model - Grounded (CWM-G)

    Maintains grounded physical/sensor state representation.
    Processes sensor data from Talos and provides low-level
    physical state information.

    The CWM-G operates on grounded representations:
    - Sensor readings (camera, depth, IMU, force sensors)
    - Physical entity positions and orientations
    - Real-time state updates from hardware

    In Phase 1, this works with simulated sensor data.
    In Phase 2+, this will integrate with real Talos hardware.

    Attributes:
        sensor_data: Current sensor readings
        physical_state: Current physical state representation
        sensor_fusion_enabled: Whether sensor fusion is active
    """

    def __init__(self):
        """Initialize the Grounded World Model with empty state"""
        self.sensor_data: dict[str, SensorReading] = {}
        self.physical_state: dict[str, Any] = {}
        self.sensor_fusion_enabled: bool = False

    def update_from_sensors(self, sensor_readings: list[SensorReading]) -> None:
        """
        Update grounded state from sensor readings.

        Processes new sensor data and updates the physical state representation.
        In Phase 2, this will include sensor fusion algorithms.

        Args:
            sensor_readings: List of new sensor readings

        Note:
            Phase 1: Simple storage of sensor data
            Phase 2+: Sensor fusion, filtering, uncertainty handling
        """
        for reading in sensor_readings:
            sensor_id = f"{reading.sensor_type.value}_{reading.timestamp}"
            self.sensor_data[sensor_id] = reading

        # TODO: Implement sensor fusion in Phase 2
        # This will combine multiple sensor readings to estimate
        # physical state with uncertainty

    def query_physical_state(self, entity_id: str) -> dict[str, Any] | None:
        """
        Query physical state of an entity.

        Args:
            entity_id: Unique identifier of the entity

        Returns:
            Physical state information (position, orientation, velocity, etc.)
            or None if entity is not tracked

        Example:
            >>> cwm_g.query_physical_state("robot_arm")
            {"position": [x, y, z], "orientation": [qw, qx, qy, qz], "velocity": [vx, vy, vz]}
        """
        return self.physical_state.get(entity_id)

    def update_physical_state(self, entity_id: str, state: dict[str, Any]) -> None:
        """
        Update physical state of an entity.

        Args:
            entity_id: Unique identifier of the entity
            state: New physical state information
        """
        self.physical_state[entity_id] = state

    def get_latest_sensor_reading(self, sensor_type: SensorType) -> SensorReading | None:
        """
        Get the most recent reading from a specific sensor type.

        Args:
            sensor_type: Type of sensor to query

        Returns:
            Most recent SensorReading or None if no data available
        """
        readings = [
            r for r in self.sensor_data.values()
            if r.sensor_type == sensor_type
        ]
        if not readings:
            return None
        return max(readings, key=lambda r: r.timestamp)

    def enable_sensor_fusion(self) -> None:
        """
        Enable sensor fusion for multi-modal state estimation.

        Note:
            This is a Phase 2 feature. Currently a stub.
        """
        # TODO: Implement sensor fusion in Phase 2
        self.sensor_fusion_enabled = True

    def ground_abstract_entity(self, entity_id: str, abstract_state: dict[str, Any]) -> dict[str, Any]:
        """
        Ground an abstract entity to physical state.

        Bridges CWM-A (abstract) and CWM-G (grounded) by mapping
        abstract entities to physical coordinates and properties.

        Args:
            entity_id: Entity identifier from abstract model
            abstract_state: Abstract state representation

        Returns:
            Grounded physical state representation

        Note:
            This is a key integration point between CWM-A and CWM-G
        """
        # TODO: Implement abstract-to-grounded mapping
        # This will use the HCG to map abstract concepts to
        # physical sensor data and coordinates
        return {}
