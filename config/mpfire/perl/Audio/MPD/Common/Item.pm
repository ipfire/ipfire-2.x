#
# This file is part of Audio::MPD::Common
# Copyright (c) 2007 Jerome Quelin, all rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself.
#
#

package Audio::MPD::Common::Item;

use strict;
use warnings;
use Audio::MPD::Common::Item::Directory;
use Audio::MPD::Common::Item::Playlist;
use Audio::MPD::Common::Item::Song;

#our ($VERSION) = '$Rev: 5645 $' =~ /(\d+)/;

#
# constructor.
#
sub new {
    my ($pkg, %params) = @_;

    # transform keys in lowercase.
    my %lowcase;
    @lowcase{ keys %params } = values %params;

    return Audio::MPD::Common::Item::Song->new(\%lowcase)      if exists $params{file};
    return Audio::MPD::Common::Item::Directory->new(\%lowcase) if exists $params{directory};
    return Audio::MPD::Common::Item::Playlist->new(\%lowcase)  if exists $params{playlist};
}

1;

__END__


=head1 NAME

Audio::MPD::Common::Item - a generic collection item


=head1 SYNOPSIS

    my $item = Audio::MPD::Common::Item->new( %params );


=head1 DESCRIPTION

C<Audio::MPD::Common::Item> is a virtual class representing a generic
item of mpd's collection. It can be either a song, a directory or a playlist.

Depending on the params given to C<new>, it will create and return an
C<Audio::MPD::Common::Item::Song>, an C<Audio::MPD::Common::Item::Directory>
or an C<Audio::MPD::Common::Playlist> object. Currently, the
discrimination is done on the existence of the C<file> key of C<%params>.


=head1 PUBLIC METHODS

Note that the only sub worth it in this class is the constructor:

=over 4

=item new( key => val [, key => val [, ...] ] )

Create and return either an C<Audio::MPD::Common::Item::Song>, an
C<Audio::MPD::Common::Item::Directory> or an C<Audio::MPD::Common::Playlist>
object, depending on the existence of a key C<file>, C<directory> or
C<playlist> (respectively).

=back


=head1 SEE ALSO

=over 4

=item L<Audio::MPD>

=item L<POE::Component::Client::MPD>

=back


=head1 AUTHOR

Jerome Quelin, C<< <jquelin at cpan.org> >>


=head1 COPYRIGHT & LICENSE

Copyright (c) 2007 Jerome Quelin, all rights reserved.

This program is free software; you can redistribute it and/or modify
it under the same terms as Perl itself.

=cut
