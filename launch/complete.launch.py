import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('rihkrover_description')
    
    # URDF and RViz files
    urdf_file = os.path.join(pkg_share, 'urdf', 'rihkrover.urdf')
    rviz_config = os.path.join(pkg_share, 'rviz', 'physical_lidar.rviz')
    
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # 1. Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_desc,
                'use_sim_time': False
            }]
        ),

	# 1.5 THE MISSING WHEEL FIX
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[{'use_sim_time': False}]
	),

        # 2. RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': False}]
        ),

        # 3. FAKE WHEELS (odom -> base_footprint)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='fake_wheels',
            arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_footprint']
        ),

        # 4. SLAM FIX BRIDGE (base_footprint -> base_link)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='slam_bridge',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link']
        )
    ])
