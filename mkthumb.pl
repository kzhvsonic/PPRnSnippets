#!/usr/bin/perl
# Image::Magick ���g���āAWordpress �̃T���l�[�������@��
# ���킹���t�@�C�����ŃT���l�[�����ꊇ�쐬�B
# �t�@�C���͈����Ŏw��
use strict;
use warnings;
use Carp;
use File::Basename;
use Image::Magick;
my $MK = new MK_THUMB;

foreach my $file (@ARGV){
	$MK->mkthumb($file,150,1,0); # thumb�͎l�p
	$MK->mkthumb($file,320,0,0); # medium ���f�t�H���g��300�����ǂ�
	$MK->mkthumb($file,800,0,0); # large
}

package MK_THUMB;
#----------------------------------------------------------
# �R���X�g���N�^
#----------------------------------------------------------
sub new {
	my $proto = shift;
	my $bgcolor = shift || '#000'; # �T���l�[���̃o�b�N�J���[
	my $class = ref($proto) || $proto;
	my $self = {
		'bgcolor' => $bgcolor,
	};
	bless $self, $class;
}

#----------------------------------------------------------
# �T���l�[���쐬
#----------------------------------------------------------
sub mkthumb {
	my $self = shift;
	my($file,$size,$square,$fill) = @_;
	my $img = new Image::Magick;
	my $warn = $img->Read($file);
	unless("$warn"){
		my($ix,$iy) = $img->Get('width','height');
		return if($ix <= $size && $iy <= $size);
		my($x,$y) = (0,0);
		if( $square and !($fill) ){ # �l�p���T���l�[��(���Ӑ؂藎�Ƃ�)
			if($ix < $iy){ # �Z���ق�����ɂ���
				$x = $size;
				$y = int($size / $ix * $iy);
			}
			else{
				$x = int($size / $iy * $ix);
				$y = $size;
			}
			$img->Resize(width=>$x,height=>$y);
			$img->Crop(width=>$size,height=>$size);
			$x = $y = $size;
		}
		else{
			if($ix > $iy){ # �����ق�����ɂ���
				$x = $size;
				$y = int($size / $ix * $iy);
			}
			else{
				$x = int($size / $iy * $ix);
				$y = $size;
			}
			$img->Resize(width=>$x,height=>$y);
			if($fill){ # �]���𖄂߂Ďl�p���T���l�[���ɂ���
				$img->Extent(gravity=>'Center',width=>$size,height=>$size,background=>$self->{bgcolor});
				$x = $y = $size;
			}
		}
		my($base,$dir,$ext) = main::fileparse($file,qr/\.[^.]*/);
		my $thumb = $dir.$base.'-'.$x.'x'.$y.$ext;
		$warn = $img->Write(filename=>$thumb); # ��������
	}
	main::carp( $warn ) if $warn;
}
