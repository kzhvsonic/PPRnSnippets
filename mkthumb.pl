#!/usr/bin/perl
# Image::Magick を使って、Wordpress のサムネール命名法に
# あわせたファイル名でサムネールを一括作成。
# ファイルは引数で指定
use strict;
use warnings;
use Carp;
use File::Basename;
use Image::Magick;
my $MK = new MK_THUMB;

foreach my $file (@ARGV){
	$MK->mkthumb($file,150,1,0); # thumbは四角
	$MK->mkthumb($file,320,0,0); # medium ＜デフォルトは300だけどね
	$MK->mkthumb($file,800,0,0); # large
}

package MK_THUMB;
#----------------------------------------------------------
# コンストラクタ
#----------------------------------------------------------
sub new {
	my $proto = shift;
	my $bgcolor = shift || '#000'; # サムネールのバックカラー
	my $class = ref($proto) || $proto;
	my $self = {
		'bgcolor' => $bgcolor,
	};
	bless $self, $class;
}

#----------------------------------------------------------
# サムネール作成
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
		if( $square and !($fill) ){ # 四角いサムネール(長辺切り落とし)
			if($ix < $iy){ # 短いほうを基準にする
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
			if($ix > $iy){ # 長いほうを基準にする
				$x = $size;
				$y = int($size / $ix * $iy);
			}
			else{
				$x = int($size / $iy * $ix);
				$y = $size;
			}
			$img->Resize(width=>$x,height=>$y);
			if($fill){ # 余白を埋めて四角いサムネールにする
				$img->Extent(gravity=>'Center',width=>$size,height=>$size,background=>$self->{bgcolor});
				$x = $y = $size;
			}
		}
		my($base,$dir,$ext) = main::fileparse($file,qr/\.[^.]*/);
		my $thumb = $dir.$base.'-'.$x.'x'.$y.$ext;
		$warn = $img->Write(filename=>$thumb); # 書き込み
	}
	main::carp( $warn ) if $warn;
}
