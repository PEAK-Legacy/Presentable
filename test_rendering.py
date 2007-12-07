from peak.ui import rendering
from unittest import TestCase
class Fixture(object): pass

class SkinTests(TestCase):

    def setUp(self):
        class test_sheet(rendering.Defaults):
            a = 1
            b = 2
        self.sheet = test_sheet
        self.skin = self.sheet()

    def testStylesheetBasics(self):
        self.failUnless(
            isinstance(self.skin, self.sheet) and
            isinstance(self.sheet, rendering.StyleSheet) and
            issubclass(rendering.StyleSheet, type)
        )
        self.assertEqual(self.skin.sheet, self.sheet)

    def testSubskinType(self):
        class s1(rendering.Defaults): pass
        class s2(s1): pass
        class s3(rendering.Defaults): pass
        for ss in [s1], [s2], [s3], [s2, s1], [s3,s1], [s2,s1,s3]:
            ts = self.skin.subskin(*ss)
            for s in ss: self.failUnless(isinstance(ts, s))
        for ss in [s1, s2], [s3, s1, s2]:
            self.assertRaises(TypeError, self.skin.subskin, *ss)

    def testSkinsWithAttrs(self):
        self.assertEqual(self.skin.a, 1)
        self.assertEqual(self.skin.b, 2)
        aSkin = self.sheet(a=2, b=1)
        self.assertEqual(aSkin.a, 2)
        self.assertEqual(aSkin.b, 1)
        skin2 = aSkin.subskin()
        self.assertEqual(skin2.a, 2)
        self.assertEqual(skin2.b, 1)

    def testSkinAttrChecking(self):
        self.assertRaises(TypeError, self.sheet, x=1)

    def testRuleCascading(self):
        sheet = rendering.StyleSheet('demo', (), {})
        self.assertEqual(list(sheet[Fixture]), [])
        self.failIf(Fixture in sheet)
        sheet[Fixture] = test = lambda: 42
        self.failUnless(Fixture in sheet)
        self.assertEqual(list(sheet[Fixture]), [test])
        self.assertRaises(KeyError, sheet.__setitem__, Fixture, test)

        sheet2 = rendering.StyleSheet('sheet2', (sheet,), {})
        self.assertEqual(list(sheet2[Fixture]), [test])
        self.failUnless(Fixture in sheet2)

        class F2(Fixture): pass
        self.failUnless(F2 in sheet2)
        self.assertEqual(list(sheet2[F2]), [test])

        self.assertEqual(list(sheet2), [Fixture])
        sheet[F2] = test2 = lambda: 24
        self.assertEqual(set(sheet2), set([Fixture, F2]))
        self.assertEqual(list(sheet[F2]), [test, test2])
        self.assertEqual(list(sheet2[F2]), [test, test2])
        sheet2[F2] = test2
        self.assertEqual(list(sheet2[F2]), [test, test2])

        sheet3 = rendering.StyleSheet('sheet3', (), {})
        sheet4 = rendering.StyleSheet('sheet4', (sheet3, sheet2), {})
        sheet3[Fixture] = test3 = lambda: 99
        self.assertEqual(list(sheet4[F2]), [test, test3, test2])


































