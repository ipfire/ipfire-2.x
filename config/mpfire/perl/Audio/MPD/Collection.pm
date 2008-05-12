#
# This file is part of Audio::MPD
# Copyright (c) 2007 Jerome Quelin, all rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself.
#
#

package Audio::MPD::Collection;

use strict;
use warnings;
use Scalar::Util qw[ weaken ];

use base qw[ Class::Accessor::Fast ];
__PACKAGE__->mk_accessors( qw[ _mpd ] );


#our ($VERSION) = '$Rev: 5284 $' =~ /(\d+)/;


#--
# Constructor

#
# my $collection = Audio::MPD::Collection->new( $mpd );
#
# This will create the object, holding a back-reference to the Audio::MPD
# object itself (for communication purposes). But in order to play safe and
# to free the memory in time, this reference is weakened.
#
# Note that you're not supposed to call this constructor yourself, an
# Audio::MPD::Collection is automatically created for you during the creation
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

# -- Collection: retrieving songs & directories

#
# my @items = $collection->all_items( [$path] );
#
# Return *all* AMC::Items (both songs & directories) currently known
# by mpd.
#
# If $path is supplied (relative to mpd root), restrict the retrieval to
# songs and dirs in this directory.
#
sub all_items {
    my ($self, $path) = @_;
    $path ||= '';
    $path =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[listallinfo "$path"\n] );
}


#
# my @items = $collection->all_items_simple( [$path] );
#
# Return *all* AMC::Items (both songs & directories) currently known
# by mpd.
#
# If $path is supplied (relative to mpd root), restrict the retrieval to
# songs and dirs in this directory.
#
# /!\ Warning: the AMC::Item::Song objects will only have their tag
# file filled. Any other tag will be empty, so don't use this sub for any
# other thing than a quick scan!
#
sub all_items_simple {
    my ($self, $path) = @_;
    $path ||= '';
    $path =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[listall "$path"\n] );
}


#
# my @items = $collection->items_in_dir( [$path] );
#
# Return the items in the given $path. If no $path supplied, do it on mpd's
# root directory.
#
# Note that this sub does not work recusrively on all directories.
#
sub items_in_dir {
    my ($self, $path) = @_;
    $path ||= '';
    $path =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[lsinfo "$path"\n] );
}



# -- Collection: retrieving the whole collection

#
# my @songs = $collection->all_songs( [$path] );
#
# Return *all* AMC::Item::Songs currently known by mpd.
#
# If $path is supplied (relative to mpd root), restrict the retrieval to
# songs and dirs in this directory.
#
sub all_songs {
    my ($self, $path) = @_;
    return grep { $_->isa('Audio::MPD::Common::Item::Song') } $self->all_items($path);
}


#
# my @albums = $collection->all_albums;
#
# Return the list of all albums (strings) currently known by mpd.
#
sub all_albums {
    my ($self) = @_;
    return $self->_mpd->_cooked_command_strip_first_field( "list album\n" );
}


#
# my @artists = $collection->all_artists;
#
# Return the list of all artists (strings) currently known by mpd.
#
sub all_artists {
    my ($self) = @_;
    return $self->_mpd->_cooked_command_strip_first_field( "list artist\n" );
}


#
# my @titles = $collection->all_titles;
#
# Return the list of all titles (strings) currently known by mpd.
#
sub all_titles {
    my ($self) = @_;
    return $self->_mpd->_cooked_command_strip_first_field( "list title\n" );
}


#
# my @genre = $collection->all_genre;
#
# Return the list of all genres (strings) currently known by mpd.
#
sub all_genre {
    my ($self) = @_;
    return $self->_mpd->_cooked_command_strip_first_field( "list genre\n" );
}


#
# my @yers = $collection->all_years;
#
# Return the list of all years (strings) currently known by mpd.
#
sub all_years {
    my ($self) = @_;
    return $self->_mpd->_cooked_command_strip_first_field( "list date\n" );
}


#
# my @pathes = $collection->all_pathes;
#
# Return the list of all pathes (strings) currently known by mpd.
#
sub all_pathes {
    my ($self) = @_;
    return $self->_mpd->_cooked_command_strip_first_field( "list filename\n" );
}


#
# my @items = $collection->all_playlists;
#
# Return the list of playlists (strings) currently known by mpd.
#
sub all_playlists {
    my ($self) = @_;

    return
        map { /^playlist: (.*)$/ ? ($1) : () }
        $self->_mpd->_send_command( "lsinfo\n" );
}



# -- Collection: picking songs

#
# my $song = $collection->song( $path );
#
# Return the AMC::Item::Song which correspond to $path.
#
sub song {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    my ($item) = $self->_mpd->_cooked_command_as_items( qq[find filename "$what"\n] );
    return $item;
}


#
# my $song = $collection->songs_with_filename_partial( $path );
#
# Return the AMC::Item::Songs containing $string in their path.
#
sub songs_with_filename_partial {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[search filename "$what"\n] );
}


# -- Collection: songs, albums & artists relations

#
# my @albums = $collection->albums_by_artist($artist);
#
# Return all albums (strings) performed by $artist or where $artist
# participated.
#
sub albums_by_artist {
    my ($self, $artist) = @_;
    $artist =~ s/"/\\"/g;
    return $self->_mpd->_cooked_command_strip_first_field( qq[list album "$artist"\n] );
}


#
# my @songs = $collection->songs_by_artist( $genre );
#
# Return all AMC::Item::Songs performed in $genre.
#

sub songs_by_genre {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[find genre "$what"\n] );
}


sub filenames_by_artist {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_filename( qq[find artist "$what"\n] );
}


sub filenames_by_year {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_filename( qq[find date "$what"\n] );
}

sub filenames_by_genre {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_filename( qq[find genre "$what"\n] );
}


sub filenames_by_album {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_filename( qq[find album "$what"\n] );
}


#
# my @songs = $collection->songs_by_artist_partial( $string );
#
# Return all AMC::Item::Songs performed by an artist with $string
# in her name.
#
sub songs_by_artist_partial {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[search artist "$what"\n] );
}


#
# my @songs = $collection->songs_from_album( $album );
#
# Return all AMC::Item::Songs appearing in $album.
#
sub songs_from_album {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[find album "$what"\n] );
}


#
# my @songs = $collection->songs_from_album_partial( $string );
#
# Return all AMC::Item::Songs appearing in album containing $string.
#
sub songs_from_album_partial {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[search album "$what"\n] );
}


#
# my @songs = $collection->songs_with_title( $title );
#
# Return all AMC::Item::Songs which title is exactly $title.
#
sub songs_with_title {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[find title "$what"\n] );
}


#
# my @songs = $collection->songs_with_title_partial( $string );
#
# Return all AMC::Item::Songs where $string is part of the title.
#
sub songs_with_title_partial {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_items( qq[search title "$what"\n] );
}


# my @songs = $collection->songs_with_title_partial_filename( $string );
#
# Return all AMC::Item::Songs where $string is part of the title.
#
sub songs_with_title_partial_filename {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;


    return $self->_mpd->_cooked_command_as_filename( qq[search title "$what"\n] );
}

# my @songs = $collection->songs_with_artist_partial_filename( $string );
#
# Return all AMC::Item::Songs where $string is part of the artist.
#
sub songs_with_artist_partial_filename {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_filename( qq[search artist "$what"\n] );
}


# my @songs = $collection->songs_with_album_partial_filename( $string );
#
# Return all AMC::Item::Songs where $string is part of the album.
#
sub songs_with_album_partial_filename {
    my ($self, $what) = @_;
    $what =~ s/"/\\"/g;

    return $self->_mpd->_cooked_command_as_filename( qq[search album "$what"\n] );
}


1;

__END__


=head1 NAME

Audio::MPD::Collection - an object to query MPD's collection


=head1 SYNOPSIS

    my $song = $mpd->collection->random_song;


=head1 DESCRIPTION

C<Audio::MPD::Collection> is a class meant to access & query MPD's
collection. You will be able to use those high-level methods instead
of using the low-level methods provided by mpd itself.


=head1 PUBLIC METHODS

=head2 Constructor

=over 4

=item new( $mpd )

This will create the object, holding a back-reference to the C<Audio::MPD>
object itself (for communication purposes). But in order to play safe and
to free the memory in time, this reference is weakened.

Note that you're not supposed to call this constructor yourself, an
C<Audio::MPD::Collection> is automatically created for you during the creation
of an C<Audio::MPD> object.

=back


=head2 Retrieving songs & directories

=over 4

=item $coll->all_items( [$path] )

Return B<all> C<Audio::MPD::Common::Item>s (both songs & directories)
currently known by mpd.

If C<$path> is supplied (relative to mpd root), restrict the retrieval to
songs and dirs in this directory.


=item $coll->all_items_simple( [$path] )

Return B<all> C<Audio::MPD::Common::Item>s (both songs & directories)
currently known by mpd.

If C<$path> is supplied (relative to mpd root), restrict the retrieval to
songs and dirs in this directory.

B</!\ Warning>: the C<Audio::MPD::Common::Item::Song> objects will only have
their tag file filled. Any other tag will be empty, so don't use this sub for
any other thing than a quick scan!


=item $coll->items_in_dir( [$path] )

Return the items in the given C<$path>. If no C<$path> supplied, do it on
mpd's root directory.

Note that this sub does not work recusrively on all directories.


=back


=head2 Retrieving the whole collection

=over 4

=item $coll->all_songs( [$path] )

Return B<all> C<Audio::MPD::Common::Item::Song>s currently known by mpd.

If C<$path> is supplied (relative to mpd root), restrict the retrieval to
songs and dirs in this directory.


=item $coll->all_albums()

Return the list of all albums (strings) currently known by mpd.


=item $coll->all_artists()

Return the list of all artists (strings) currently known by mpd.


=item $coll->all_titles()

Return the list of all song titles (strings) currently known by mpd.


=item $coll->all_pathes()

Return the list of all pathes (strings) currently known by mpd.


=item $coll->all_playlists()

Return the list of all playlists (strings) currently known by mpd.


=back


=head2 Picking a song

=over 4

=item $coll->song( $path )

Return the C<Audio::MPD::Common::Item::Song> which correspond to C<$path>.


=item $coll->songs_with_filename_partial( $path )

Return the C<Audio::MPD::Common::Item::Song>s containing $string in their path.


=back


=head2 Songs, albums & artists relations

=over 4

=item $coll->albums_by_artist( $artist )

Return all albums (strings) performed by C<$artist> or where C<$artist>
participated.


=item $coll->songs_by_artist( $artist )

Return all C<Audio::MPD::Common::Item::Song>s performed by C<$artist>.


=item $coll->songs_by_artist_partial( $string )

Return all C<Audio::MPD::Common::Item::Song>s performed by an artist with
C<$string> in her name.


=item $coll->songs_from_album( $album )

Return all C<Audio::MPD::Common::Item::Song>s appearing in C<$album>.


=item $coll->songs_from_album_partial( $string )

Return all C<Audio::MPD::Common::Item::Song>s appearing in album containing C<$string>.


=item $coll->songs_with_title( $title )

Return all C<Audio::MPD::Common::Item::Song>s which title is exactly C<$title>.


=item $coll->songs_with_title_partial( $string )

Return all C<Audio::MPD::Common::Item::Song>s where C<$string> is part of the title.


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
