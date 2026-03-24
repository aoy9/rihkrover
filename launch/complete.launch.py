import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('rihkrover_description')
    
    # URDF and RViz files
    urdf_file = os.path.join(pkg_share, 'urdf', 'rihkrover1.urdf') # Using your updated urdf name
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
            parameters=[{'robot_description': robot_desc, 'use_sim_time': False}]
        ),

        # 1.5 Joint State Publisher
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher'
        ),

        # 2. RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config]
        ),

        # 3. RF2O LASER ODOMETRY (Replaces fake_wheels)
        Node(
            package='rf2o_laser_odometry',
            executable='rf2o_laser_odometry_node',
            name='rf2o_laser_odometry',
            output='screen',
            parameters=[{
                'laser_scan_topic' : '/scan',
                'odom_topic' : '/odom',
                'publish_tf' : True,
                'base_frame_id' : 'base_footprint',
                'odom_frame_id' : 'odom',
                'init_pose_from_topic' : '',
                'freq' : 10.0
            }],
        ),

        # 4. SLAM FIX BRIDGE (base_footprint -> base_link)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='slam_bridge',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link']
        ),

        # 5. LIDAR FRAME BRIDGE (In case hardware uses 'laser_frame')
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='lidar_bridge',
            arguments=['0', '0', '0', '0', '0', '0', 'laser', 'laser_frame']
        )
    ])
