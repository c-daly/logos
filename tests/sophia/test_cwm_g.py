"""
Unit tests for CWM-G (Grounded World Model) module

Tests cover:
- Sensor data management
- Physical state tracking
- Sensor reading queries
"""

from sophia.cwm_g import CWMGrounded, SensorReading, SensorType


class TestCWMGrounded:
    """Test suite for CWMGrounded class"""

    def test_initialization(self):
        """Test CWM-G initializes with empty state"""
        cwm_g = CWMGrounded()
        assert len(cwm_g.sensor_data) == 0
        assert len(cwm_g.physical_state) == 0
        assert cwm_g.sensor_fusion_enabled is False

    def test_update_from_sensors(self):
        """Test updating from sensor readings"""
        cwm_g = CWMGrounded()

        reading = SensorReading(
            sensor_type=SensorType.CAMERA,
            timestamp=1.0,
            data={"image": "test_data"},
            confidence=0.95
        )

        cwm_g.update_from_sensors([reading])

        assert len(cwm_g.sensor_data) == 1

    def test_query_physical_state(self):
        """Test querying physical state of an entity"""
        cwm_g = CWMGrounded()

        result = cwm_g.query_physical_state("test_entity")
        assert result is None

        cwm_g.update_physical_state("test_entity", {"position": [0, 0, 0]})
        result = cwm_g.query_physical_state("test_entity")

        assert result is not None
        assert "position" in result

    def test_update_physical_state(self):
        """Test updating physical state"""
        cwm_g = CWMGrounded()

        state = {"position": [1, 2, 3], "orientation": [0, 0, 0, 1]}
        cwm_g.update_physical_state("entity_1", state)

        assert cwm_g.physical_state["entity_1"] == state

    def test_get_latest_sensor_reading(self):
        """Test getting latest sensor reading by type"""
        cwm_g = CWMGrounded()

        reading1 = SensorReading(SensorType.CAMERA, 1.0, {})
        reading2 = SensorReading(SensorType.CAMERA, 2.0, {})
        reading3 = SensorReading(SensorType.DEPTH, 1.5, {})

        cwm_g.update_from_sensors([reading1, reading2, reading3])

        latest_camera = cwm_g.get_latest_sensor_reading(SensorType.CAMERA)
        assert latest_camera is not None
        assert latest_camera.timestamp == 2.0

        latest_depth = cwm_g.get_latest_sensor_reading(SensorType.DEPTH)
        assert latest_depth is not None
        assert latest_depth.timestamp == 1.5

        latest_imu = cwm_g.get_latest_sensor_reading(SensorType.IMU)
        assert latest_imu is None

    def test_enable_sensor_fusion(self):
        """Test enabling sensor fusion"""
        cwm_g = CWMGrounded()

        cwm_g.enable_sensor_fusion()

        assert cwm_g.sensor_fusion_enabled is True

    def test_ground_abstract_entity_returns_dict(self):
        """Test grounding abstract entity to physical state"""
        cwm_g = CWMGrounded()

        result = cwm_g.ground_abstract_entity("entity_1", {"type": "cup"})

        assert isinstance(result, dict)
