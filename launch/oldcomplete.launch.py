import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('rihkrover_description')
    
    # 1. Modern Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': '-r -s shapes.sdf'}.items(), # '-r' auto-plays the simulation
    )

    # URDF and RViz files
    urdf_file = os.path.join(pkg_share, 'urdf', 'rihkrover.urdf')
    rviz_config = os.path.join(pkg_share, 'rviz', 'physical_lidar.rviz')
    
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # 2. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # 3. Deleted Joint Publish node for TF error

    # 4. Spawn robot in Modern Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'rihkrover',
            '-z', '0.1' # Drops it slightly above ground
        ],
        output='screen'
    )

    # 5. ROS-GZ Bridge (Crucial for RViz and driving!)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model',
	    '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/image_raw@sensor_msgs/msg/Image[ignition.msgs.Image',
        ],
        output='screen'
    )

    # 6. RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': False}],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge,
        rviz
    ])
