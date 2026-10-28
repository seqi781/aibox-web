import pathlib
import subprocess
import tempfile
import unittest
class LegacyTest(unittest.TestCase):
 def test_obsolete_sync_cannot_modify_main_site(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);target=root/'public/aibox';target.mkdir(parents=True)
   sentinel=target/'sentinel.txt';sentinel.write_text('must remain')
   (root/'package.json').write_text('{"dependencies":{"next":"synthetic"}}')
   (root/'next.config.ts').write_text('export default {};')
   script=pathlib.Path(__file__).parents[2]/'nextjs/sync.sh'
   result=subprocess.run(['bash',str(script),str(root)],capture_output=True)
   self.assertEqual(result.returncode,2)
   self.assertEqual(sentinel.read_text(),'must remain')
if __name__=='__main__':unittest.main()
