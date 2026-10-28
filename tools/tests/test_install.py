import json
import hashlib
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]))
from install_release import install, verify
from package import PUBLIC_FILES
class InstallTest(unittest.TestCase):
 def test_atomic_selection_rollback_and_manifest_rejection(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp).resolve(); source=root/'package';source.mkdir(); manifest={}
   for name in PUBLIC_FILES:
    p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('synthetic')
    manifest[name]=hashlib.sha256(p.read_bytes()).hexdigest()
   a='a'*40;b='b'*40
   (source/'release.json').write_text(json.dumps({'revision':a,'files':manifest}))
   deploy=root/'aibox'
   self.assertIsNone(install(deploy,a,source)['previous'])
   (source/'release.json').write_text(json.dumps({'revision':b,'files':manifest}))
   self.assertEqual(install(deploy,b,source)['previous'],'releases/'+a)
   self.assertEqual(install(deploy,a)['previous'],'releases/'+b)
   (source/'assets/site.js').write_text('tampered')
   with self.assertRaises(ValueError):verify(source,b)
   self.assertEqual((deploy/'current').resolve(),deploy/'releases'/a)
   with self.assertRaises(ValueError):install('/opt/usehooo',a)
if __name__=='__main__':unittest.main()
