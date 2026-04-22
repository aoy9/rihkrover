from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='camera_ros',
            executable='camera_node',
            name='camera',
            output='screen',
            respawn=True,           # The safety net: auto-restarts on crash
            respawn_delay=2.0,      # Gives the hardware 2 seconds to release the lock
            parameters=[
                {'width': 320},
                {'height': 240},
                {'format': 'YUYV'},
                {'fps': 5},
                # Force Best Effort QoS for both raw and compressed streams over Wi-Fi
                {'qos_overrides./camera/image_raw.publisher.reliability': 'best_effort'},
                {'qos_overrides./camera/image_raw/compressed.publisher.reliability': 'best_effort'}
            ]
        )
    ])
