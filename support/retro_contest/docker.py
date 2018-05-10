import argparse
import docker
import io
import os
import random
import requests.exceptions
import sys
import tempfile
import threading
try:
    from retro import data_path
except ImportError:
    def data_path():
        raise RuntimeError('Could not find Gym Retro data directory')


class LogThread:
    def __init__(self, container):
        self._log = container.logs(stdout=True, stderr=True, stream=True)
        self._thread = threading.Thread(target=self._run)
        self._active = False

    def start(self):
        if self._active:
            return
        self._active = True
        self._thread.start()

    def exit(self):
        self._active = False

    def _run(self):
        while self._active:
            try:
                print(next(self._log).decode('utf-8'), end='')
            except StopIteration:
                break


def convert_path(path):
    if sys.platform.startswith('win') and path[1] == ':':
        path = '/%s%s' % (path[0].lower(), path[2:].replace('\\', '/'))
    return path


def run(game_state_strs, entry=None, **kwargs):
    game_state_pairs = []
    for game_state_str in game_state_strs:
        words = game_state_str.split(':')
        if len(words) >= 1:
            game_state_pair = (words[0], None)
            if len(words) >= 2:
                game_state_pair[1] = words[1]
            game_state_pairs.append(game_state_pair)

    client = docker.from_env()
<<<<<<< HEAD
    remote_command_prefix = ['retro-contest-remote', 'run']
    remote_command_suffix = ['-b', 'results/bk2', '-m', 'results']
=======

    remote_commands = []
    for game, state in zip(str.split(game), str.split(state)):
        remote_commands.append(['retro-contest-remote', 'run', game, *([state] if state else []), '-b', 'results/bk2', '-m', 'results'])
>>>>>>> TheAggregator/master
    remote_name = kwargs.get('remote_env', 'openai/retro-env')
    num_envs = kwargs.get('num_envs', 1)
    agent_command = []
    agent_name = kwargs.get('agent', 'agent')

    if kwargs.get('wallclock_limit') is not None:
<<<<<<< HEAD
        remote_command_suffix.extend(['-W', str(kwargs['wallclock_limit'])])
    if kwargs.get('timestep_limit') is not None:
        remote_command_suffix.extend(['-T', str(kwargs['timestep_limit'])])
    if kwargs.get('discrete_actions'):
        remote_command_suffix.extend(['-D'])
=======
        map(lambda x: x.extend(['-W', str(kwargs['wallclock_limit'])]), remote_commands)
    if kwargs.get('timestep_limit') is not None:
        map(lambda x: x.extend(['-T', str(kwargs['timestep_limit'])]), remote_commands)
    if kwargs.get('discrete_actions'):
        map(lambda x: x.extend(['-D']), remote_commands)
>>>>>>> TheAggregator/master

    if entry:
        agent_command.append(entry)
        if kwargs.get('entry_args'):
            agent_command.extend(kwargs['entry_args'])

<<<<<<< HEAD
    rand = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 8))
    volname_prefix = 'retro-contest-tmp%s' % rand
=======
>>>>>>> TheAggregator/master
    datamount = {}
    agentmount = {}
    if kwargs.get('resultsdir'):
        results = os.path.realpath(kwargs['resultsdir'])
        datamount[convert_path(results)] = {'bind': '/root/compo/results'}
        os.makedirs(results, exist_ok=True)
    else:
        results = None

    if kwargs.get('agentdir'):
        agentdir = os.path.realpath(kwargs['agentdir'])
        agentmount[convert_path(agentdir)] = {'bind': '/root/compo/out'}
        os.makedirs(agentdir, exist_ok=True)

    container_kwargs = {'detach': True, 'network_disabled': True}
    remote_kwargs = dict(container_kwargs)
    agent_kwargs = dict(container_kwargs)

    if kwargs.get('agent_shm'):
        agent_kwargs['shm_size'] = kwargs['agent_shm']

    if kwargs.get('use_host_data'):
<<<<<<< HEAD
        remote_command_prefix = [remote_command_prefix[0], '--data-dir', '/root/data', *remote_command_prefix[1:]]
        datamount[convert_path(data_path())] = {'bind': '/root/data', 'mode': 'ro'}

    remotes = []
    bridges = []
    volnames = []
    for i, (game, state) in enumerate(game_state_pairs):
        volname = '%s-%n' % (volname_prefix, i)
        volnames.append(volname)
        bridges.append(client.volumes.create(volname, driver='local', driver_opts={'type': 'tmpfs', 'device': 'tmpfs'}))
        remote_command = [*remote_command_prefix, game, *([state] if state else []), *remote_command_suffix]
        try:
            remote = client.containers.run(remote_name, remote_command,
                                           volumes={volname: {'bind': '/root/compo/tmp'},
                                                    **datamount},
                                           **remote_kwargs)
        except:
            for remote in remotes:
                remote.kill()
                remote.remove()
            for bridge in bridges:
                bridge.remove()
            raise
        remotes.append(remote)

    try:
        volmounts = {}
        for i, volname in enumerate(volnames):
            volmounts[volname] = {'bind': '/root/compo/tmp%n' % i}
        agent = client.containers.run(agent_name, agent_command,
                                      volumes={**volmounts, **agentmount},
                                      runtime=kwargs.get('runtime', 'nvidia'),
                                      **agent_kwargs)
    except:
        for remote in remotes:
            remote.kill()
            remote.remove()
        for bridge in bridges:
            bridge.remove()
        raise

    a_exit = None
    r_exits = [None for _ in remotes]
=======
        remote_commands = list(map(lambda x: [x[0], '--data-dir', '/root/data', *x[1:]], remote_commands))
        datamount[convert_path(data_path())] = {'bind': '/root/data', 'mode': 'ro'}

    remotes = []
    socket_vols = []

    def remove_remotes():
        for remote in remotes:
            try:
                remote.kill()
            except:
                pass
            try:
                remote.remove(v=True)
            except:
                pass

    def remove_socket_vols():
        for socket_vol in socket_vols:
            try:
                socket_vol.remove()
            except:
                pass

    try:
        for i in range(num_envs):
            rand = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 8))
            volname = 'retro-contest-tmp%s' % rand
            socket_vol = client.volumes.create(volname, driver='local', driver_opts={'type': 'tmpfs', 'device': 'tmpfs'})
            socket_vols.append(socket_vol)
            print("Remote command " + str(i) + " " + str(remote_commands[i]))
            remote = client.containers.run(remote_name, remote_commands[i],
                                           volumes={volname: {'bind': '/root/compo/tmp/sock'}, **datamount},
                                           **remote_kwargs)
            remotes.append(remote)
    except:
        remove_socket_vols()
        raise

    try:
        volumes = {volume.name: {'bind': '/root/compo/tmp/sock{0}'.format(i)} for i, volume in enumerate(socket_vols)}
        agent = client.containers.run(agent_name, agent_command,
                                      volumes={**volumes, **agentmount},
                                      runtime=kwargs.get('runtime', 'nvidia'),
                                      **agent_kwargs)
    except:
        remove_remotes()
        remove_socket_vols()
        raise

    a_exit = None
    r_exits = [None] * len(remotes)
>>>>>>> TheAggregator/master

    if not kwargs.get('quiet'):
        log_thread = LogThread(agent)
        log_thread.start()

    try:
        while True:
            try:
                a_exit = agent.wait(timeout=5)
                break
            except requests.exceptions.RequestException:
                pass
<<<<<<< HEAD
            for i, remote in enumerate(remotes):
                try:
                    r_exits[i] = remote.wait(timeout=5)
                    break
                except requests.exceptions.RequestException:
                    pass
=======

            found_server_error = False
            for i, remote in enumerate(remotes):
                try:
                    r_exits[i] = remote.wait(timeout=5)
                    found_server_error = True
                except requests.exceptions.RequestException:
                    pass
            if found_server_error:
                break
>>>>>>> TheAggregator/master

        if a_exit is None:
            try:
                a_exit = agent.wait(timeout=10)
            except requests.exceptions.RequestException:
                agent.kill()
<<<<<<< HEAD
        for i, remote in enumerate(remotes):
            if r_exits[i] is None:
=======

        for i, (r_exit, remote) in enumerate(zip(r_exits, remotes)):
            if r_exit is None:
>>>>>>> TheAggregator/master
                try:
                    r_exits[i] = remote.wait(timeout=10)
                except requests.exceptions.RequestException:
                    remote.kill()
    except:
        if a_exit is None:
            try:
                a_exit = agent.wait(timeout=1)
            except:
                try:
                    agent.kill()
                except docker.errors.APIError:
                    pass
<<<<<<< HEAD
        for i, remote in enumerate(remotes):
            if r_exits[i] is None:
=======

        for i, (r_exit, remote) in enumerate(zip(r_exits, remotes)):
            if r_exit is None:
>>>>>>> TheAggregator/master
                try:
                    r_exits[i] = remote.wait(timeout=1)
                except:
                    try:
                        remote.kill()
                    except docker.errors.APIError:
                        pass
<<<<<<< HEAD
=======

>>>>>>> TheAggregator/master
        raise
    finally:
        if isinstance(a_exit, dict):
            a_exit = a_exit.get('StatusCode')
<<<<<<< HEAD
        for r_exit in r_exits:
            if isinstance(r_exit, dict):
                r_exit = r_exit.get('StatusCode')
=======
        for i, r_exit in enumerate(r_exits):
            if isinstance(r_exit, dict):
                r_exits[i] = r_exit.get('StatusCode')
>>>>>>> TheAggregator/master

        if not kwargs.get('quiet'):
            log_thread.exit()

        remote_logs = {'remote{0}'.format(i): (r_exit, remote.logs(stdout=True, stderr=False), remote.logs(stdout=False, stderr=True)) for i, (r_exit, remote) in enumerate(zip(r_exits, remotes))}
        logs = {
<<<<<<< HEAD
=======
            **remote_logs,
>>>>>>> TheAggregator/master
            'agent': (a_exit, agent.logs(stdout=True, stderr=False), agent.logs(stdout=False, stderr=True))
        }

        for i, remote in enumerate(remotes):
            logs['remote%n' % i] = (r_exits[i], remote.logs(stdout=True, stderr=False), remote.logs(stdout=False, stderr=True))


        if results:
<<<<<<< HEAD
            for log_name, (_, log_out, log_err) in logs.items():
                with open(os.path.join(results, '%s-stdout.txt' % log_name), 'w') as f:
                    f.write(log_out.decode('utf-8'))
                with open(os.path.join(results, '%s-stderr.txt' % log_name), 'w') as f:
                    f.write(log_err.decode('utf-8'))

        for remote in remotes:
            remote.remove()
        agent.remove()
        for bridge in bridges:
            bridge.remove()
=======
            for i in range(len(remotes)):
                with open(os.path.join(results, 'remote{0}-stdout.txt'.format(i)), 'w') as f:
                    f.write(logs['remote{0}'.format(i)][1].decode('utf-8'))
                with open(os.path.join(results, 'remote{0}-stderr.txt'.format(i)), 'w') as f:
                    f.write(logs['remote{0}'.format(i)][2].decode('utf-8'))
            with open(os.path.join(results, 'agent-stdout.txt'), 'w') as f:
                f.write(logs['agent'][1].decode('utf-8'))
            with open(os.path.join(results, 'agent-stderr.txt'), 'w') as f:
                f.write(logs['agent'][2].decode('utf-8'))

        remove_remotes()
        agent.remove(v=True)
        remove_socket_vols()
>>>>>>> TheAggregator/master

    return logs


def run_multi_env_args(args):
    kwargs = {
        'entry_args': args.args,
        'wallclock_limit': args.wallclock_limit,
        'timestep_limit': args.timestep_limit,
        'discrete_actions': args.discrete_actions,
        'resultsdir': args.results_dir,
        'agentdir': args.agent_dir,
        'quiet': args.quiet,
        'use_host_data': args.use_host_data,
        'agent_shm': args.agent_shm,
    }

    if args.no_nv:
        kwargs['runtime'] = None

    if args.agent:
        kwargs['agent'] = args.agent

    if args.remote_env:
        kwargs['remote_env'] = args.remote_env

<<<<<<< HEAD
    results = run(args.game_state_pairs, args.entry, **kwargs)
    exited_cleanly = True
    for log_name, (exit_code, _, _) in results:
        if exit_code:
            exited_cleanly = False
            print('%s exited uncleanly:' % log_name, exit_code)
    return exited_cleanly


def run_args(args):
    args.game_state_pairs = ['%s:%s' % (args.game, args.state)]
    return run_multi_env_args(args)
=======
    num_envs = args.num_envs if args.num_envs else 1
    kwargs['num_envs'] = num_envs

    results = run(args.game, args.state, args.entry, **kwargs)

    exited_cleanly = True

    a_exit = results['agent'][0]
    if a_exit:
        print('Agent exited uncleanly', a_exit)
        exited_cleanly = False

    for i in range(num_envs):
        r_exit = results['remote{0}'.format(i)][0]
        if r_exit:
            print('Remote {0} exited uncleanly:'.format(i), r_exit)
            exited_cleanly = False

    return exited_cleanly
>>>>>>> TheAggregator/master


def build(path, tag, install=None, pass_env=False):
    from pkg_resources import EntryPoint
    import tarfile
    if install:
        destination = 'module'
    else:
        destination = 'agent.py'
    docker_file = ['FROM openai/retro-agent',
                   'COPY context %s' % destination]

    if not install:
        docker_file.append('CMD ["python", "-u", "/root/compo/agent.py"]')
    else:
        docker_file.append('RUN . ~/venv/bin/activate && pip install -e module')
        valid = not any(c in install for c in ' "\\')
        if pass_env:
            try:
                EntryPoint.parse('entry=' + install)
            except ValueError:
                valid = False
            if not valid:
                raise ValueError('Invalid entry point')
            docker_file.append('CMD ["retro-contest-agent", "%s"]' % install)
        else:
            if not valid:
                raise ValueError('Invalid module name')
            docker_file.append('CMD ["python", "-u", "-m", "%s"]' % install)

    print('Creating Docker image...')
    docker_file_full = io.BytesIO('\n'.join(docker_file).encode('utf-8'))
    client = docker.from_env()
    with tempfile.NamedTemporaryFile() as f:
        tf = tarfile.open(mode='w:gz', fileobj=f)
        docker_file_info = tarfile.TarInfo('Dockerfile')
        docker_file_info.size = len(docker_file_full.getvalue())
        tf.addfile(docker_file_info, docker_file_full)
        tf.add(path, arcname='context', exclude=lambda fname: fname.endswith('/.git'))
        tf.close()
        f.seek(0)
        client.images.build(fileobj=f, custom_context=True, tag=tag, gzip=True)
    print('Done!')


def build_args(args):
    kwargs = {
        'install': args.install,
        'pass_env': args.pass_env,
    }

    try:
        build(args.path, args.tag, **kwargs)
    except docker.errors.BuildError as be:
        print(*[log['stream'] for log in be.build_log if 'stream' in log])
        raise
    return True


def init_parser(subparsers):
    parser_run = subparsers.add_parser('run', description='Run Docker containers locally')
    parser_run.set_defaults(func=run_args)
    parser_run.add_argument('game', type=str, help='Name of the game to run')
    parser_run.add_argument('state', type=str, default=None, nargs='?', help='Name of initial state')
    parser_run.add_argument('--entry', '-e', type=str, help='Name of agent entry point')
    parser_run.add_argument('--args', '-A', type=str, nargs='+', help='Extra agent entry arguments')
    parser_run.add_argument('--agent', '-a', type=str, help='Extra agent Docker image')
    parser_run.add_argument('--wallclock-limit', '-W', type=float, default=None, help='Maximum time to run in seconds')
    parser_run.add_argument('--timestep-limit', '-T', type=int, default=None, help='Maximum time to run in timesteps')
    parser_run.add_argument('--no-nv', '-N', action='store_true', help='Disable Nvidia runtime')
    parser_run.add_argument('--num-envs', '-n', type=int, default=None, help='Number of remote environments')
    parser_run.add_argument('--remote-env', '-R', type=str, help='Remote Docker image')
    parser_run.add_argument('--results-dir', '-r', type=str, help='Path to output results')
    parser_run.add_argument('--agent-dir', '-o', type=str, help='Path to mount into agent (mounted at /root/compo/out)')
    parser_run.add_argument('--discrete-actions', '-D', action='store_true', help='Use a discrete action space')
    parser_run.add_argument('--use-host-data', '-d', action='store_true', help='Use the host Gym Retro data directory')
    parser_run.add_argument('--quiet', '-q', action='store_true', help='Disable printing agent logs')
    parser_run.add_argument('--agent-shm', type=str, help='Agent /dev/shm size')

    parser_run_multi_env = subparsers.add_parser('run-multi-env', description='Run Docker containers locally, using multiple environments with one agent')
    parser_run_multi_env.set_defaults(func=run_multi_env_args)
    parser_run_multi_env.add_argument('game_state_pairs', type=str, nargs='+' help='List of one or more game-state pairs to run, each one of the form "game:state"')
    parser_run_multi_env.add_argument('--entry', '-e', type=str, help='Name of agent entry point')
    parser_run_multi_env.add_argument('--args', '-A', type=str, nargs='+', help='Extra agent entry arguments')
    parser_run_multi_env.add_argument('--agent', '-a', type=str, help='Extra agent Docker image')
    parser_run_multi_env.add_argument('--wallclock-limit', '-W', type=float, default=None, help='Maximum time to run in seconds')
    parser_run_multi_env.add_argument('--timestep-limit', '-T', type=int, default=None, help='Maximum time to run in timesteps')
    parser_run_multi_env.add_argument('--no-nv', '-N', action='store_true', help='Disable Nvidia runtime')
    parser_run_multi_env.add_argument('--remote-env', '-R', type=str, help='Remote Docker image')
    parser_run_multi_env.add_argument('--results-dir', '-r', type=str, help='Path to output results')
    parser_run_multi_env.add_argument('--agent-dir', '-o', type=str, help='Path to mount into agent (mounted at /root/compo/out)')
    parser_run_multi_env.add_argument('--discrete-actions', '-D', action='store_true', help='Use a discrete action space')
    parser_run_multi_env.add_argument('--use-host-data', '-d', action='store_true', help='Use the host Gym Retro data directory')
    parser_run_multi_env.add_argument('--quiet', '-q', action='store_true', help='Disable printing agent logs')
    parser_run_multi_env.add_argument('--agent-shm', type=str, help='Agent /dev/shm size')

    parser_build = subparsers.add_parser('build', description='Build agent Docker containers')
    parser_build.set_defaults(func=build_args)
    parser_build.add_argument('path', type=str, help='Path to a file or package')
    parser_build.add_argument('--tag', '-t', required=True, type=str, help='Tag name for the built image')
    parser_build.add_argument('--install', '-i', type=str, help='Install as a package and run specified module or entry point (if -e is specified)')
    parser_build.add_argument('--pass-env', '-e', action='store_true', help='Pass preconfigured environment to entry point specified by -i')


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Run OpenAI Retro Contest support code')
    parser.set_defaults(func=lambda args: parser.print_help())
    init_parser(parser.add_subparsers())
    args = parser.parse_args(argv)
    if not args.func(args):
        sys.exit(1)


if __name__ == '__main__':
    main()
