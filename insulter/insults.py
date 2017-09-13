import random
import os

# print generated insult for the 'user'
def get_insult(insults_pref, insults_postfs='.'):
    insults_config = yaml.load(open(os.path.dirname(__file__) + '\insults.yml'))
    column1 = [
        'artless',
        'bawdy',
        'beslubbering',
        'bootless',
        'churlish',
        'cockered',
        'clouted',
        'craven',
        'currish',
        'dankish',
        'dissembling',
        'droning',
        'errant',
        'fawning',
        'fobbing',
        'froward',
        'frothy',
        'gleeking',
        'goatish',
        'gorbellied',
        'impertinent',
        'infectious',
        'jarring',
        'loggerheaded',
        'lumpish',
        'mammering',
        'mangled',
        'mewling',
        'paunchy',
        'pribbling',
        'puking',
        'puny',
        'qualling',
        'rank',
        'reeky',
        'roguish',
        'ruttish',
        'saucy',
        'spleeny',
        'spongy',
        'surly',
        'tottering',
        'unmuzzled',
        'vain',
        'venomed',
        'villainous',
        'warped',
        'wayward',
        'weedy',
        'yeasty']
    column2 = [
        'base-court',
        'bat-fowling',
        'beef-witted',
        'beetle-headed',
        'boil-brained',
        'clapper-clawed',
        'clay-brained',
        'common-kissing',
        'crook-pated',
        'dismal-dreaming',
        'dizzy-eyed',
        'doghearted',
        'dread-bolted',
        'earth-vexing',
        'elf-skinned',
        'fat-kidneyed',
        'fen-sucked',
        'flap-mouthed',
        'fly-bitten',
        'folly-fallen',
        'fool-born',
        'full-gorged',
        'guts-griping',
        'half-faced',
        'hasty-witted',
        'hedge-born',
        'hell-hated',
        'idle-headed',
        'ill-breeding',
        'ill-nurtured',
        'knotty-pated',
        'milk-livered',
        'motley-minded',
        'onion-eyed',
        'plume-plucked',
        'pottle-deep',
        'pox-marked',
        'reeling-ripe',
        'rough-hewn',
        'rude-growing',
        'rump-fed',
        'shard-borne',
        'sheep-biting',
        'spur-galled',
        'swag-bellied',
        'tardy-gaited',
        'tickle-brained',
        'toad-spotted',
        'unchin-snouted',
        'weather-bitten']
    column3 = [
        'apple-john',
        'baggage',
        'barnacle',
        'bladder',
        'boar-pig',
        'bugbear',
        'bum-bailey',
        'canker-blossom',
        'clack-dish',
        'clotpole',
        'coxcomb',
        'codpiece',
        'death-token',
        'dewberry',
        'flap-dragon',
        'flax-wench',
        'flirt-gill',
        'foot-licker',
        'fustilarian',
        'giglet',
        'gudgeon',
        'haggard',
        'harpy',
        'hedge-pig',
        'horn-beast',
        'hugger-mugger',
        'joithead',
        'lewdster',
        'lout',
        'maggot-pie',
        'malt-worm',
        'mammet',
        'measle',
        'minnow',
        'miscreant',
        'moldwarp',
        'mumble-news',
        'nut-hook',
        'pigeon-egg',
        'pignut',
        'puttock',
        'pumpion',
        'ratsbane',
        'scut',
        'skainsmate',
        'strumpet',
        'varlot',
        'vassal',
        'whey-face',
        'wagtail']
    insults_col1 = column1[random.randrange(len(column1))]
    insults_col2 = column2[random.randrange(len(column2))]
    insults_col3 = column3[random.randrange(len(column3))]
    return insults_pref + ' ' + insults_col1 + ' ' + insults_col2 + ' ' + insults_col3 + insults_postfs
