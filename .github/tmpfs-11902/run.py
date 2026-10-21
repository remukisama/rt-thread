import argparse, pathlib, subprocess, threading, time, re
p=argparse.ArgumentParser();p.add_argument('--arch',default='aarch64');p.add_argument('--bsp',default='bsp/qemu-virt64-aarch64');p.add_argument('--qemu');p.add_argument('--user',action='store_true');p.add_argument('--expect-failure',action='store_true');a=p.parse_args()
bsp=pathlib.Path(a.bsp).resolve();output=pathlib.Path('tmpfs-11902-qemu.log');data=bytearray()
cmd=[a.qemu or 'qemu-system-'+a.arch,'-M','virt' if a.arch=='aarch64' else 'vexpress-a9','-kernel','rtthread.bin','-display','none','-monitor','none','-serial','stdio']
if a.arch=='aarch64':cmd+=['-cpu','max','-smp','4','-m','128M','-append','console=ttyAMA0 earlycon cma=8M coherent_pool=2M root=vda0 rootfstype=elm rootwait rw','-drive','if=none,file='+'sd.bin'+',format=raw,id=blk0','-device','virtio-blk-device,drive=blk0']
else:cmd+=['-drive','file='+'sd.bin'+',format=raw,if=sd']
proc=subprocess.Popen(cmd,cwd=bsp,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0)
def read():
 while True:
  c=proc.stdout.read(1)
  if not c:return
  data.extend(c)
t=threading.Thread(target=read,daemon=True);t.start()
def wait_for(pattern,seconds=90,start=0):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  s=data[start:].decode(errors='replace')
  if re.search(pattern,s):return s
  if proc.poll() is not None:break
  time.sleep(.1)
 raise RuntimeError('Timed out waiting for '+pattern)
def send(command):
 for c in (command+'\n').encode():proc.stdin.write(bytes([c]));proc.stdin.flush();time.sleep(.04)
try:
 wait_for(r'msh />');time.sleep(.5);start=len(data);send('utest_run components.dfs.tmpfs_truncate')
 result=wait_for(r'\[==========\].*finished|assertion failed',120,start)
 if a.expect_failure:
  assert 'assertion failed' in result.lower() or re.search(r'\[\s*FAILED\s*\]',result), 'Unpatched baseline unexpectedly passed'
  print('EXPECTED BASELINE FAILURE CONFIRMED')
 else:
  assert not re.search(r'\[\s*FAILED\s*\]|assertion failed|TC init failed|TC cleanup failed',result,re.I), 'Regression test failed'
  assert re.search(r'\[\s*PASSED\s*\].*components.dfs.tmpfs_truncate',result), 'No passing testcase result found'
  if a.user:
   send('sys_log 1');time.sleep(.4);user_start=len(data);send('/truncate.elf');result=wait_for(r'\[USER\] PASS|\[USER\] FAIL|assertion failed',60,user_start)
   assert '[USER] PASS' in result,'User-space syscall test failed'
  print('TMPFS TRUNCATE VALIDATION PASSED')
finally:
 if proc.poll() is None:proc.terminate()
 try:proc.wait(timeout=5)
 except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
 t.join(timeout=2);s=data.decode(errors='replace');output.write_text(s,encoding='utf-8');print(s)
