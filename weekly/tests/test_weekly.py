import json
import tempfile
import unittest
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from weekly.generate_weekly import release_groups, ROOT, REPO
from weekly.selection_rules import question_plan, EXPECTED_TYPES
from weekly.build_weekly import build
from weekly.publish_local import publish
from weekly.rotation import rotated_pool
from weekly.week_key import current_week_key
from weekly.archive_reader import load_previous

class WeeklyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((REPO/'config.json').read_text())
        cls.bank=json.loads((REPO/'question_bank.json').read_text())
        cls.order=json.loads((ROOT/'curriculum_order.json').read_text())
        cls.names=[x['topic'] for x in sorted(cls.order,key=lambda x:x['sequence'])]

    def check_quiz(self,q,groups,plan):
        self.assertEqual(q['status'],'preview_only')
        questions=q['questions']
        self.assertEqual(len(questions),10)
        self.assertEqual(len({x['id'] for x in questions}),10)
        self.assertEqual(Counter(x['difficulty'] for x in questions),EXPECTED_TYPES)
        self.assertEqual([sum(x['kk'] in g for x in questions) for g in groups],
                         list(map(len,plan)))
        newest=groups[-1][-1]
        expected=len(plan[-1]) if len(groups[-1])==1 else 2
        self.assertEqual(sum(x['kk']==newest for x in questions),expected)
        self.assertTrue(all(x['kk'] in sum(groups,[]) for x in questions))

    def test_current_released_topics(self):
        _,g=release_groups(self.config,self.order)
        q=build(week='2026-W43',history=[])
        self.check_quiz(q,g,question_plan(15))

    def test_1_to_20_released_topics(self):
        for n in range(1,21):
            with self.subTest(n=n):
                config={'released':[{'name':t,'status':'released'} for t in self.names[:n]]}
                _,g=release_groups(config,self.order)
                q=build(week='2027-W02',history=[],config=config,bank=self.bank)
                self.check_quiz(q,g,question_plan(n))

    def test_six_weeks_rotation(self):
        previous=[]
        for n in range(1,7):
            week=f'2026-W{n+35:02d}'
            q=build(week=week,history=previous)
            prev_ids={v['id'] for b in previous for v in b}
            ids={v['id'] for v in q['questions']}
            self.assertFalse(ids & prev_ids)
            previous.append(q['questions'])

    def test_same_week_deterministic(self):
        a=build(week='2027-W05',history=[])
        b=build(week='2027-W05',history=[])
        self.assertEqual(a['questions'],b['questions'])

    def test_archive_rotation(self):
        with tempfile.TemporaryDirectory() as d:
            for n,status in [(38,'published'),(39,'preview_only'),(40,'published'),(42,'published')]:
                content={'week':f'2026-W{n:02d}', 'status':status,
                         'questions':[{'id':f'{n}-{i}','kk':'Example'} for i in range(10)]}
                Path(d,f'{n}.json').write_text(json.dumps(content))
            h=load_previous('2026-W41',d)
            self.assertEqual(len(h),2)
            self.assertEqual(len(load_previous('2026-W41',d,limit=1)),1)

    def test_publisher_does_not_overwrite(self):
        week=current_week_key()
        q=build(week=week,history=[])
        with tempfile.TemporaryDirectory() as d:
            preview=Path(d,'preview.json')
            preview.write_text(json.dumps(q))
            archive=Path(d,'archive')
            first=publish(preview,archive)
            published=json.loads(first.read_text())
            self.assertEqual(published['questions'],q['questions'])
            self.assertEqual(published['status'],'published')
            with self.assertRaises(FileExistsError):publish(preview,archive)
            self.assertEqual(json.loads(first.read_text()),published)
            self.assertEqual(json.loads(preview.read_text())['status'],'preview_only')

    def test_melbourne_time_zone(self):
        # Sunday 13:30 UTC is Monday 00:30 Melbourne during AEDT.
        now=datetime(2026,10,25,13,30,tzinfo=timezone.utc)
        self.assertEqual(current_week_key(now),'2026-W44')

if __name__=='__main__':unittest.main()
