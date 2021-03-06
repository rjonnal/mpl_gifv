from __future__ import print_function
from subprocess import call,Popen,PIPE
import os,glob,random,sys
import shutil
import logging
logging.basicConfig(level=logging.INFO)


try:
    p = Popen(['convert','--version'], stdout=PIPE)
    output,err = p.communicate('')
    rc = p.returncode
    assert output.decode('UTF-8').lower().find('imagemagick')>-1
    im_installed = True
except:
    im_installed = False
    
try:
    assert im_installed
    print('ImageMagick installed.')
except AssertionError as ae:
    print('Trouble finding ImageMagick convert function.')
    print(output)
    raise ImportError
    
class GIF:

    def __init__(self,gif_filename,fps=30,dpi=100,loop=0,autoclean=True,transparent=False):
        """Create a GIF object.

        Argument:
        gif_filename -- the name of the GIF file to output with GIF.make()
        Keyword arguments:
        fps -- frames per second, default 30
        dpi -- dots per inch, default 100
        loop -- how many times to loop, default 0 (infinite)
        autoclean -- clean up temporary files, default False
        """       
        self.logger = logging.getLogger(__name__)
        self.gif_filename = gif_filename
        self.fps = fps
        self.loop = loop
        self.wdir = '%s_%d.tmp'%(self.gif_filename,random.randint(0,2**32))
        self.transparent=transparent
        # generate a random working directory name; if it exists already, make
        # a new one.
        while os.path.exists(self.wdir):
            self.wdir = '%s_%d.tmp'%(self.gif_filename,random.randint(0,2**32))

        self.logger.info('Creating temporary directory %s.'%self.wdir)
        os.mkdir(self.wdir)
            
        self.index = 0
        self.dpi = dpi
        self.autoclean = autoclean
        self.frame_string = 'frame_%09d.png'
        
    def __del__(self):
        if self.autoclean:
            if os.path.exists(self.wdir):
                try:
                    self.logger.info('abnormal exit, deleting %s.'%self.wdir)
                    png_list = glob.glob(os.path.join(self.wdir,'*.png'))
                    for png_file in png_list:
                        os.remove(png_file)

                    # clean up working directory
                    os.rmdir(self.wdir)

                except Exception as e:
                    print(e)
                
    def add(self,fig):
        """Add a frame to a GIF.

        Argument:
        fig -- the handle of a matplotlib figure
        """       
        # save the given figure to the working directory
        outfn = os.path.join(self.wdir,self.frame_string%self.index)
        self.logger.info('Saving figure to file %s.'%outfn)
        try:
            fig.savefig(outfn,dpi=self.dpi,facecolor=fig.get_facecolor(),edgecolor='none',transparent=self.transparent)
        except Exception as e:
            fig.savefig(outfn)
        self.index = self.index + 1
        
    def make(self,make_gif=True,make_webm=False,verbose=False,make_script=False,delete_first=False,round_trip=False,preview_frame_index=None):
        """Make the GIF.
        """       

        # convert FPS into IM's delay parameter (expressed in 10 ms "ticks")
        delay = 1.0/float(self.fps)*100.0

        # run ImageMagick convert function to make the GIF
        self.logger.info('Running ImageMagick convert to create gif in %s.'%self.gif_filename)

        flist = glob.glob(os.path.join(self.wdir,'frame*.png'))
        flist.sort()
        if delete_first:
            os.remove(flist[0])

        if preview_frame_index is not None:
            png_filename = self.gif_filename.replace('.gif','')+'.png'
            shutil.copyfile(flist[preview_frame_index],png_filename)
            
        if round_trip:
            flist = flist + flist[::-1]

        command = ['convert','-delay','%0.1f'%delay,'-loop','%d'%self.loop]+flist+['%s'%self.gif_filename]
        #command = ['convert','-delay','%0.1f'%delay,'-loop','%d'%self.loop,'%s'%(os.path.join(self.wdir,'frame*.png')),'%s'%self.gif_filename]
        
        if verbose:
            command = command[:1]+['-verbose']+command[1:]
        if make_script:
            folder,filename = os.path.split(self.gif_filename)
            script_fn = os.path.join(folder,'make_'+os.path.splitext(filename)[0]+'.sh')
            print(script_fn)
            fid = open(script_fn,'w')
            fid.write('#! /bin/bash\n\n')
            fid.write(' '.join(command))
            fid.write('\n')
            fid.close()
        if make_gif:
            call(command)

        if make_webm:
            webm_filename = os.path.splitext(self.gif_filename)[0]+'.webm'
            self.logger.info('Running ImageMagick convert to create gif in %s.'%webm_filename)

            #-lossless 1 is causing dropped frames; not sure why
            #command = ['ffmpeg','-y','-framerate','%d'%self.fps,'-f','image2','-i',os.path.join(self.wdir,self.frame_string),'-c:v','libvpx-vp9','-pix_fmt','yuva420p','-lossless','1',webm_filename]
            command = ['ffmpeg','-y','-framerate','%d'%self.fps,'-f','image2','-i',os.path.join(self.wdir,self.frame_string),'-c:v','libvpx-vp9','-pix_fmt','yuva420p',webm_filename]
            call(command)
        
        if self.autoclean:
            self.logger.info('Cleaning up.')
            # clean up temporary png files
            png_list = glob.glob(os.path.join(self.wdir,'*.png'))
            for png_file in png_list:
                os.remove(png_file)

            # clean up working directory
            os.rmdir(self.wdir)
        
