#
# This file is part of Audio::MPD
# Copyright (c) 2007 Jerome Quelin, all rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself.
#
#

package Audio::MPD::Playlist;

use strict;
use warnings;
use Scalar::Util qw[ weaken ];

use base qw[ Class::Accessor::Fast ];
__PACKAGE__->mk_accessors( qw[ _mpd ] );


#our ($VERSION) = '$Rev$' =~ /(\d+)/;


#--
# Constructor

#
# my $collection = Audio::MPD::Playlist->new( $mpd );
#
# This will create the object, holding a back-reference to the Audio::MPD
# object itself (for communication purposes). But in order to play safe and
# to free the memory in time, this reference is weakened.
#
# Note that you're not supposed to call this constructor yourself, an
# Audio::MPD::Playlist is automatically created for you during the creation
# of an Audio::MPD object.
#
sub new {
    my ($pkg, $mpd) = @_;

    my $self = { _mpd => $mpd };
    weaken( $self->{_mpd} );
    bless $self, $pkg;
    return $self;
}


#--
# Public methods

# -- Playlist: retrieving information

#
# my @items = $pl->as_items;
#
# Return an array of AMC::Item::Songs, one for each of the
# songs in the current playlist.
#
sub as_items {
    my ($self) = @_;

    my @list = $self->_mpd->_cooked_command_as_items("playlistinfo\n");
    return @list;
}


#
# my @items = $pl->items_changed_since( $plversion );
#
# Return a list with all the songs (as API::Song objects) added to
# the playlist since playlist $plversion.
#
sub items_changed_since {
    my ($self, $plid) = @_;
    return $self->_mpd->_cooked_command_as_items("plchanges $plid\n");
}



# -- Playlist: adding / removing songs

#
# $pl->add( $path [, $path [...] ] );
#
# Add the songs identified by $path (relative to MPD's music directory) to
# the current playlist. No return value.
#
sub add {
    my ($self, @pathes) = @_;
    my $command =
          "command_list_begin\n"
        . join( '', map { s/"/\\"/g; qq[add "$_"\n] } @pathes )
        . "command_list_end\n";
    $self->_mpd->_send_command( $command );
}


#
# $pl->delete( $song [, $song [...] ] );
#
# Remove song number $song (starting from 0) from the current playlist. No
# return value.
#
sub delete {
    my ($self, @songs) = @_;
    my $command =
          "command_list_begin\n"
        . join( '', map { s/"/\\"/g; "delete $_\n" } @songs )
        . "command_list_end\n";
    $self->_mpd->_send_command( $command );
}


#
# $pl->deleteid( $songid [, $songid [...] ]);
#
# Remove the specified $songid (as assigned by mpd when inserted in playlist)
# from the current playlist. No return value.
#
sub deleteid {
    my ($self, @songs) = @_;
    my $command =
          "command_list_begin\n"
        . join( '', map { "deleteid $_\n" } @songs )
        . "command_list_end\n";
    $self->_mpd->_send_command( $command );
}


#
# $pl->clear;
#
# Remove all the songs from the current playlist. No return value.
#
sub clear {
    my ($self) = @_;
    $self->_mpd->_send_command("clear\n");
}


#
# $pl->crop;
#
#  Remove all of the songs from the current playlist *except* the current one.
#
sub crop {
    my ($self) = @_;

    my $status = $self->_mpd->status;
    my $cur = $status->song;
    my $len = $status->playlistlength - 1;

    my $command =
          "command_list_begin\n"
        . join( '', map { $_  != $cur ? "delete $_\n" : '' } reverse 0..$len )
        . "command_list_end\n";
    $self->_mpd->_send_command( $command );
}


# -- Playlist: changing playlist order

#
# $pl->shuffle();
#
# Shuffle the current playlist. No return value.
#
sub shuffle {
    my ($self) = @_;
    $self->_mpd->_send_command("shuffle\n");
}


#
# $pl->swap( $song1, $song2 );
#
# Swap positions of song number $song1 and $song2 in the current playlist.
# No return value.
#
sub swap {
    my ($self, $from, $to) = @_;
    $self->_mpd->_send_command("swap $from $to\n");
}


#
# $pl->swapid( $songid1, $songid2 );
#
# Swap the postions of song ID $songid1 with song ID $songid2 in the
# current playlist. No return value.
#
sub swapid {
    my ($self, $from, $to) = @_;
    $self->_mpd->_send_command("swapid $from $to\n");
}


#
# $pl->move( $song, $newpos );
#
# Move song number $song to the position $newpos. No return value.
#
sub move {
    my ($self, $song, $pos) = @_;
    $self->_mpd->_send_command("move $song $pos\n");
}


#
# $pl->moveid( $songid, $newpos );
#
# Move song ID $songid to the position $newpos. No return value.
#
sub moveid {
    my ($self, $song, $pos) = @_;
    $self->_mpd->_send_command("moveid $song $pos\n");
}


# -- Playlist: managing playlists

#
# $pl->load( $playlist );
#
# Load list of songs from specified $playlist file. No return value.
#
sub load {
    my ($self, $playlist) = @_;
    $self->_mpd->_send_command( qq[load "$playlist"\n] );
}


#
# $pl->save( $playlist );
#
# Save the current playlist to a file called $playlist in MPD's playlist
# directory. No return value.
#
sub save {
    my ($self, $playlist) = @_;
    $self->_mpd->_send_command( qq[save "$playlist"\n] );
}


#
# $pl->rm( $playlist )
#
# Delete playlist named $playlist from MPD's playlist directory. No
# return value.
#
sub rm {
    my ($self, $playlist) = @_;
    $self->_mpd->_send_command( qq[rm "$playlist"\n] );
}



1;

__END__


=head1 NAME

Audio::MPD::Playlist - an object to mess MPD's playlist


=head1 SYNOPSIS

    my $song = $mpd->playlist->randomize;


=head1 DESCRIPTION

C<Audio::MPD::Playlist> is a class meant to access & update MPD's
playlist.


=head1 PUBLIC METHODS

=head2 Constructor

=over 4

=item new( $mpd )

This will create the object, holding a back-reference to the C<Audio::MPD>
object itself (for communication purposes). But in order to play safe and
to free the memory in time, this reference is weakened.

Note that you're not supposed to call this constructor yourself, an
C<Audio::MPD::Playlist> is automatically created for you during the creation
of an C<Audio::MPD> object.

=back


=head2 Retrieving information

=over 4

=item $pl->as_items()

Return an array of C<Audio::MPD::Common::Item::Song>s, one for each of the
songs in the current playlist.


=item $pl->items_changed_since( $plversion )

Return a list with all the songs (as AMC::Item::Song objects) added to
the playlist since playlist $plversion.


=back


=head2 Adding / removing songs

=over 4

=item $pl->add( $path [, $path [...] ] )

Add the songs identified by C<$path> (relative to MPD's music directory) to the
current playlist. No return value.


=item $pl->delete( $song [, $song [...] ] )

Remove song number C<$song>s (starting from 0) from the current playlist. No
return value.


=item $pl->deleteid( $songid [, $songid [...] ] )

Remove the specified C<$songid>s (as assigned by mpd when inserted in playlist)
from the current playlist. No return value.


=item $pl->clear()

Remove all the songs from the current playlist. No return value.


=item $pl->crop()

Remove all of the songs from the current playlist *except* the
song currently playing.


=back


=head2 Changing playlist order

=over 4

=item $pl->shuffle()

Shuffle the current playlist. No return value.


=item $pl->swap( $song1, $song2 )

Swap positions of song number C<$song1> and C<$song2> in the current
playlist. No return value.


=item $pl->swapid( $songid1, $songid2 )

Swap the postions of song ID C<$songid1> with song ID C<$songid2> in the
current playlist. No return value.


=item $pl->move( $song, $newpos )

Move song number C<$song> to the position C<$newpos>. No return value.


=item $pl->moveid( $songid, $newpos )

Move song ID C<$songid> to the position C<$newpos>. No return value.


=back


=head2 Managing playlists

=over 4

=item $pl->load( $playlist )

Load list of songs from specified C<$playlist> file. No return value.


=item $pl->save( $playlist )

Save the current playlist to a file called C<$playlist> in MPD's playlist
directory. No return value.


=item $pl->rm( $playlist )

Delete playlist named C<$playlist> from MPD's playlist directory. No
return value.


=back


=head1 SEE ALSO

L<Audio::MPD>


=head1 AUTHOR

Jerome Quelin, C<< <jquelin at cpan.org> >>


=head1 COPYRIGHT & LICENSE

Copyright (c) 2007 Jerome Quelin, all rights reserved.

This program is free software; you can redistribute it and/or modify
it under the same terms as Perl itself.

=cut
