import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler, TimerAction

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import xacro

from osrf_pycommon.terminal_color import ansi

def generate_launch_description():

    description_pkg_path = os.path.join(get_package_share_directory('fusionbot_description'))
    gazebo_model_path = os.path.join(description_pkg_path, 'models')

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += ":" + gazebo_model_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = gazebo_model_path

    print(ansi("yellow"), "If it's your 1st time to download Gazebo model on your computer, it may take few minutes to finish.", ansi("reset"))

    # Joint State Publisher
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # Prepare Robot State Publisher Params
    urdf_file = os.path.join(description_pkg_path, 'urdf', 'fusionbot_description.urdf')

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[urdf_file],
    )

    # Launch RViz
    rviz_config_file = os.path.join(description_pkg_path, 'rviz', 'description.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    return LaunchDescription([
        joint_state_publisher_gui,
        robot_state_publisher,
        TimerAction(    
            period=3.0,
            actions=[rviz]
        ),
    ])