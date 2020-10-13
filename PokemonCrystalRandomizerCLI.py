import sys
import os
import collections
import argparse
import datetime
import yaml
import json
import random
import string
from shutil import copyfile

import RunCustomRandomizationAssumedFill as RunCustomRandomization


class PokemonItemRandomizerCLI:

    def __init__(self):
        self.setup = 'Test'
        self.settings = self.load_settings('Modes/Standard.yml')
        self.modList = []
        self.presets = self.grab_presets()

    def get_rng_seed(self):
        seed = input('What is the seed? Press Enter for a random seed.')
        if not seed:
            seed = str(datetime.datetime.now())
        random.seed(a=seed, version=2)
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    
    def load_settings(self, settings_file):
        with open(settings_file, 'r') as fp:
            return yaml.load(fp.read(), Loader=yaml.FullLoader)
    
    def load_modifiers(self, modifier_list):
        result = []
        for modifier in modifier_list:
            with open(modifier, 'r') as fp:
                result.append(yaml.load(fp.read(), Loader=yaml.FullLoader))
        
        return result

    def grab_presets(self):
        presets = [preset.replace('.yml', '') for preset in os.listdir('./Modes') if '.yml' in preset]
        return presets
    
    def select_preset(self):
        presets = dict(zip(range(len(self.presets)), self.presets))
        preset_selection = False

        print('Select a preset:\n')
        for key, value in presets.items():
            print(f'[{key}] - {value}')
        while preset_selection is False:
            selection = input('Enter Preset number: ').strip()
            try:
                chosen_preset = presets[int(selection)]
                preset_selection = True
            except KeyError:
                print('Selected preset is not part of the list.\n')
        
        return chosen_preset

    def get_rom(self):
        success = False
        while success is False:
            rom_path = input('What is the file path to the Crystal Speedchoice ROM? Drag and drop the ROM file into Terminal. \n').strip()
            if rom_path.endswith('.gbc'):
                rom_file = os.path.basename(rom_path)
                success = True
            else:
                print('The file is not a .gbc file. Please either enter the path to the ROM or drag the ROM into Terminal.\n')
        
        return [rom_file, rom_path]
    
    def generate_randomized_rom(self, input_rom_file, input_rom_path, spoilers, seed):
        now = datetime.datetime.now()
        output_file_name = f'{now.strftime("%Y-%m-%d-%H%M")}.gbc'
        copyfile(input_rom_path, f'./Outputs/{output_file_name}')
        output_file_path = f'./Outputs/{output_file_name}'

        yamltext = self.settings['BasePatch']
        with open(self.settings['BasePatch'], 'r') as fp:
            patches = json.load(fp)
        self.modList = self.load_modifiers(self.settings['DefaultModifiers'])

        tlv = 0
        wlv = 0
        print(self.modList)

        if 'ProgressItems' in self.settings:
            if 'CoreProgress' in self.settings:
                result = RunCustomRandomization.randomizeRom(output_file_path,self.settings['Goal'], self.settings['FlagsSet'],patches, banList = self.settings['BannedLocations'], allowList = self.settings['AllowedLocations'], modifiers = self.modList,adjustTrainerLevels = False, adjustRegularWildLevels = False, adjustSpecialWildLevels = False, trainerLVBoost = tlv, wildLVBoost=wlv, requiredItems = self.settings['ProgressItems'],coreProgress = self.settings['coreProgress'], otherSettings = self.settings)
            else:
                result = RunCustomRandomization.randomizeRom(output_file_path,self.settings['Goal'], self.settings['FlagsSet'],patches, banList = self.settings['BannedLocations'], allowList = self.settings['AllowedLocations'], modifiers = self.modList,adjustTrainerLevels = False, adjustRegularWildLevels = False, adjustSpecialWildLevels = False, trainerLVBoost = tlv, wildLVBoost=wlv, requiredItems = self.settings['ProgressItems'], otherSettings = self.settings)
        else:
            if 'CoreProgress' in self.settings:
                result = RunCustomRandomization.randomizeRom(output_file_path,self.settings['Goal'], self.settings['FlagsSet'],patches, banList = self.settings['BannedLocations'], allowList = self.settings['AllowedLocations'], modifiers = self.modList,adjustTrainerLevels = False, adjustRegularWildLevels = False, adjustSpecialWildLevels = False, trainerLVBoost = tlv, wildLVBoost=wlv,coreProgress = self.settings['coreProgress'], otherSettings = self.settings)
            else:
                result = RunCustomRandomization.randomizeRom(output_file_path,self.settings['Goal'], self.settings['FlagsSet'],patches, banList = self.settings['BannedLocations'], allowList = self.settings['AllowedLocations'], modifiers = self.modList,adjustTrainerLevels = False, adjustRegularWildLevels = False, adjustSpecialWildLevels = False, trainerLVBoost = tlv, wildLVBoost=wlv, otherSettings = self.settings)

        if spoilers:
            output_spoiler = {}
            output_spoiler['RNG Seed'] = seed
            output_spoiler['Solution'] = result[1]
            output_spoiler['Useless Stuff'] = result[4]

            with open(f'./Outputs/{output_file_name}_SPOILER_LOG.txt', 'w') as fp:
                yaml.dump(output_spoiler, fp, default_flow_style = False)
        
        
    def main(self):
        seed = self.get_rng_seed()
        print(f'RNG Seed is: {seed}')

        user_preset = self.select_preset()
        self.settings = self.load_settings(f'Modes/{user_preset}.yml')
        print(self.settings)

        spoiler_choice = input('Do you want a spoiler log file? Y/n \n').strip()
        if not spoiler_choice:
            spoilers = True
        else:
            try:
                options = dict(zip(['y','n'], [True, False]))
                spoilers = options[spoiler_choice.lower()]
            except KeyError:
                print('Choice of spoilers unintelligible. Generating spoiler log by default.')
                spoilers = True

        rom_file, rom_path = self.get_rom()
        self.generate_randomized_rom(rom_file, rom_path, spoilers, seed)

if __name__ == '__main__':
    cli = PokemonItemRandomizerCLI()
    cli.main()
