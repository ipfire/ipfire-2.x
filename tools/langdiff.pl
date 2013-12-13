#!/usr/bin/perl

my @one=();
my @two=();

my $file1;
my $file2;
my $cnt=0;
my $numArgs = $#ARGV + 1;
if ($numArgs !=2 ){
	print"Usage:  langdiff.pl <languagefile1 - incomplete> <languagefile2 - complete>\n";
	exit;
}else{
	$file1=$ARGV[0];
	$file2=$ARGV[1];
}

open(FILE1, $file1) or die 'Unable to open file $file1.';
my @one = <FILE1>;
close(FILE1);
undef ($one[0]);
undef ($one[1]);
undef ($one[2]);
undef ($one[3]);
undef ($one[$#one-1]);
undef ($one[$#one-2]);
open(FILE2, $file2) or die 'Unable to open file $file2.';
my @two = <FILE2>;
close(FILE2);
undef ($two[0]);
undef ($two[1]);
undef ($two[2]);
undef ($two[3]);
undef ($two[$#two-1]);
undef ($two[$#two-2]);
open(FILE3, ">language-diff.txt") or die 'Unable to open config file.';

foreach my $line (@two){
	my ($a,$b) = split ("=>",$line);
	if(!&is_in_array($a)){
		$cnt++;
		print FILE3 "$a => $b";
	}
}

sub is_in_array{
	my $val = shift;

	foreach my $line1 (@one){
		my ($c,$d) = split ("=>",$line1);
		return 1 if ($val eq $c);
	}
	return 0;
}


print"$cnt lines from $file2 are not existent in $file1. Please check language-diff.txt for details.\n\n";
