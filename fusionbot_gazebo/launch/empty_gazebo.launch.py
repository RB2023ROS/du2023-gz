import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch.actions import SetEnvironmentVariable
from launch.substitutions import Command, EnvironmentVariable, PathJoinSubstitution, FindExecutable

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from osrf_pycommon.terminal_color import ansi

def generate_launch_description():

    # Prepare Robot State Publisher Params
    description_pkg_path = os.path.join(get_package_share_directory('fusionbot_gazebo'))
    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')   

    # Start Gazebo serverPathJoinSubstitution
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        # launch_arguments={'world': world_path}.items()
    )

    # Start Gazebo client    
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))
    )

    # Robot State Publisher
    # Method 1 - using xacro
    xacro_file = os.path.join(description_pkg_path, 'urdf', 'fusionbot.urdf.xacro')
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            xacro_file,
            " ",
            "name:=fusionbot",
            " ",
            "prefix:=''",
            " ",
            "is_sim:=true",
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    # Method 2 - using urdf
    # urdf_file = os.path.join(description_pkg_path, 'urdf', 'fusionbot.urdf')

    # doc = xacro.parse(open(urdf_file))
    # xacro.process_doc(doc)
    # robot_description = {'robot_description': doc.toxml()}

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}, robot_description],
    )

    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    # Spawn Robot
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'fusionbot'],
                        output='screen')

    return LaunchDescription([
        start_gazebo_server_cmd,
        start_gazebo_client_cmd,
        joint_state_publisher,
        robot_state_publisher,
        spawn_entity,
    ])
