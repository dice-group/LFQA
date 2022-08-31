'''
This python file helps decide on available docker-compose profiles, based on the configuration.ini file.
It is called from 'start_docker_containers.sh'
'''
import configparser, json, sys


def detect_components(config_file):
    '''
    Function to detect required components in the configuration files.
    '''
    config = configparser.ConfigParser()
    config.read(config_file)
    comp_set = set()
    for section in config:
        if section.strip().lower().startswith("eamt pipeline"):
            comp_set.update(json.loads(config.get(section, 'components')))
    return comp_set


# Should be comma separated string of docker profiles
profile_str = ''
component_set = detect_components('configuration.ini')
profile_arr = []
if 'mag_el' in component_set:
    profile_arr.append('mag')
if 'libre_mt' in component_set:
    profile_arr.append('libre_mt')
if 'opus_mt' in component_set:
    profile_arr.append('opus_mt')
profile_str = ','.join(profile_arr)
# Return the string to the shell, to be stored in COMPOSE_PROFILES variable
print(profile_str)
sys.exit(0)
