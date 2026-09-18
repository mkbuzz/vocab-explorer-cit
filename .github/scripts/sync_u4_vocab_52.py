from pathlib import Path
import json, re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

m = re.search(r'const ITEMS = (\[.*?\]);\nconst STORAGE_KEY', s, re.S)
if not m:
    raise RuntimeError('Could not find ITEMS data')
items = json.loads(m.group(1))
by_id = {x['id']: x for x in items}

# Remove entries deleted from the revised U4 Vocab sheet.
for obsolete in ['in-2010', 'so-many-from-that', 'make-money']:
    by_id.pop(obsolete, None)

# The revised sheet now presents this pattern without an initial A placeholder.
if 'become-interested' in by_id:
    by_id['become-interested']['term'] = 'become interested in B'

# New item: predator. Core meaning/example/synonyms follow the revised U4 Vocab sheet.
by_id['predator'] = {
    'id':'predator',
    'term':'predator',
    'pos':'n',
    'enMeaning':'an animal that hunts and eats other animals',
    'jpMeaning':'捕食者, 捕食動物',
    'examples':[
        {'en':'Lions are <strong>predators</strong> that hunt other animals.','jp':'ライオンは他の動物を狩る捕食者である。'},
        {'en':'Large <strong>predators</strong> help keep the ecosystem balanced.','jp':'大型の捕食者は生態系のバランスを保つのに役立つ。'},
        {'en':'A shark is a <strong>predator</strong> that hunts other sea animals.','jp':'サメは他の海の生き物を狩る捕食者である。'},
        {'en':'Wolves are <strong>predators</strong> that often hunt in groups.','jp':'オオカミは群れで狩りをすることが多い捕食者である。'},
        {'en':'Small animals often hide from <strong>predators</strong>.','jp':'小さな動物は捕食者から身を隠すことが多い。'}
    ],
    'longExamples':[
        {'en':'Many <strong>predators</strong> hunt weaker animals, which helps keep animal populations from growing too large.','jp':'多くの捕食者は弱い動物を狩り, 動物の個体数が増えすぎるのを防ぐのに役立つ。'},
        {'en':'When large <strong>predators</strong> disappear from an ecosystem, the number of smaller animals can increase quickly.','jp':'生態系から大型の捕食者がいなくなると, 小さな動物の数が急速に増えることがある。'},
        {'en':'Some fish avoid <strong>predators</strong> by staying close to rocks or other places where they can hide.','jp':'魚の中には, 岩などの隠れられる場所の近くにいることで捕食者を避けるものもいる。'}
    ],
    'wordFamily':'(n) predator, predation; (adj) predatory',
    'related':['hunter','hunting animal','carnivore'],
    'relatedLabel':'Synonyms',
    'jpPos':'名'
}

# New item: for centuries. Core meaning/example/similar expressions follow the revised U4 Vocab sheet.
by_id['for-centuries'] = {
    'id':'for-centuries',
    'term':'for centuries',
    'pos':'phr',
    'enMeaning':'for hundreds of years',
    'jpMeaning':'何世紀もの間, 何百年もの間',
    'examples':[
        {'en':'People have lived in this town <strong>for centuries</strong>.','jp':'人々は何世紀もの間, この町に住んできた。'},
        {'en':'This tradition has continued <strong>for centuries</strong>.','jp':'この伝統は何世紀もの間続いている。'},
        {'en':'The same family has lived here <strong>for centuries</strong>.','jp':'同じ一族が何世紀もの間ここに住んできた。'},
        {'en':'People have used this road <strong>for centuries</strong>.','jp':'人々は何世紀もの間この道を使ってきた。'},
        {'en':'The castle has stood on this hill <strong>for centuries</strong>.','jp':'その城は何世紀もの間この丘に建っている。'}
    ],
    'longExamples':[
        {'en':'People have depended on rivers for food and transportation <strong>for centuries</strong>, long before modern roads were built.','jp':'近代的な道路が造られるずっと前から, 人々は何世紀もの間, 食料や交通のために川に頼ってきた。'},
        {'en':'This farming method has been used <strong>for centuries</strong>, although modern machines have changed how much work people must do.','jp':'この農法は何世紀もの間使われてきたが, 現代の機械によって人々がしなければならない作業量は変わった。'},
        {'en':'The temple has welcomed visitors <strong>for centuries</strong> and remains an important part of the local community today.','jp':'その寺は何世紀もの間訪問者を迎えており, 今日でも地域社会の重要な一部である。'}
    ],
    'wordFamily':'',
    'related':['for hundreds of years','over the centuries','for many centuries'],
    'relatedLabel':'Similar expressions',
    'jpPos':'句'
}

desired_ids = [
    'diverse','species','commercial','quantity','estimate','reduce','double','stable','restore','survive',
    'major-factor','maintain','communities','traditional','target','locate','equipment','enable','predator',
    'publish','journal','prediction','reproduce','throughout-history','today','however','for-centuries','mid-20th',
    'response','result','addition','particular','without-them','for-example','think-as','signs-has',
    'cannot-quickly-enough','become-interested','source-of','these-include','enable-a-to-b','estimate-that',
    'mainly-due','greatly-reduced','plenty','more-than-doubled','largely-because','serious-problems',
    'make-prediction','another-way','give-chance','future-with'
]
missing = [x for x in desired_ids if x not in by_id]
if missing:
    raise RuntimeError(f'Missing expected item IDs: {missing}')
new_items = [by_id[x] for x in desired_ids]
if len(new_items) != 52:
    raise RuntimeError(f'Expected 52 items, got {len(new_items)}')

s = s[:m.start(1)] + json.dumps(new_items, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]

# Avoid a brief stale count before JS refreshes the UI.
s = s.replace('0 / 53 words viewed', '0 / 52 words viewed')

# Count only currently active vocabulary when preserving old browser progress.
s = s.replace(
    'const learned=Object.values(state.wordMarks||{}).filter(x=>x==="learned").length;',
    'const learned=ITEMS.filter(x=>(state.wordMarks||{})[x.id]==="learned").length;'
)

# If a browser has a saved random order from the old 53-item list, regenerate it for the current 52-item list.
old_random = '''  else if(state.sort==="random"){\n    const rank=new Map(state.shuffle.map((id,i)=>[id,i]));\n    arr.sort((a,b)=>(rank.get(a.id)??999)-(rank.get(b.id)??999));\n  }'''
new_random = '''  else if(state.sort==="random"){\n    const validIds=new Set(ITEMS.map(x=>x.id));\n    if(!Array.isArray(state.shuffle) || state.shuffle.length!==ITEMS.length || state.shuffle.some(id=>!validIds.has(id))) shuffleIds();\n    const rank=new Map(state.shuffle.map((id,i)=>[id,i]));\n    arr.sort((a,b)=>(rank.get(a.id)??999)-(rank.get(b.id)??999));\n  }'''
if old_random in s:
    s = s.replace(old_random, new_random, 1)

path.write_text(s, encoding='utf-8')
print('Synced Vocabulary Explorer to the revised 52-item U4 list.')
