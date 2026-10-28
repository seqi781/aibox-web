import importlib.util
import pathlib
import subprocess
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('pack',pathlib.Path(__file__).parents[1]/'package.py')
pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
class PackageTest(unittest.TestCase):
 def test_whitelist_versioned_assets_and_no_overwrite(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp)/'repo';root.mkdir()
   subprocess.run(['git','init','-q',str(root)],check=True)
   for name in pack.PUBLIC_FILES:
    p=root/name;p.parent.mkdir(exist_ok=True,parents=True)
    p.write_text('<link href="../assets/site.css"><script src="cast.js"></script>' if name.endswith('.html') else 'synthetic')
   (root/'.env').write_text('DO_NOT_PUBLISH=synthetic')
   subprocess.run(['git','-C',str(root),'add','.'],check=True)
   subprocess.run(['git','-C',str(root),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture'],check=True)
   revision=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
   out=pathlib.Path(tmp)/'release';manifest=pack.package(root,revision,out)
   self.assertEqual(set(manifest),set(pack.PUBLIC_FILES))
   self.assertFalse((out/'.env').exists())
   self.assertIn('/aibox/_assets/'+revision+'/assets/site.css',(out/'en/index.html').read_text())
   self.assertIn('/aibox/_assets/'+revision+'/init/cast.js',(out/'init/index.html').read_text())
   with self.assertRaises(ValueError):pack.package(root,revision,out)
   with self.assertRaises(ValueError):pack.package(root,'main',out/'other')
if __name__=='__main__':unittest.main()
