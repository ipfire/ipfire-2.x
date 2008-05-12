#
# This file is part of Audio::MPD::Common
# Copyright (c) 2007 Jerome Quelin, all rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself.
#
#

package Audio::MPD::Common::Item::Song;

use strict;
use warnings;

use overload '""' => \&as_string;
use Readonly;

use base qw[ Class::Accessor::Fast Audio::MPD::Common::Item ];
__PACKAGE__->mk_accessors( qw[ Album Artist file id pos Title Track time ] );

#our ($VERSION) = '$Rev: 5645 $' =~ /(\d+)/;

Readonly my $SEP => ' = ';


#
# my $str = $song->as_string;
#
# Return a string representing $song. This string will be;
#  - either "Album = Track = Artist = Title"
#  - or     "Artist = Title"
#  - or     "Title"
#  - or     "file"
# (in this order), depending on the existing tags of the song. The last
# possibility always exist of course, since it's a path.
#
sub as_string {
    my ($self) = @_;

    return $self->file unless defined $self->Title;
    my $str = $self->Title;
    return $str unless defined $self->Artist;
    $str = $self->Artist . $SEP . $str;
    return $str unless defined $self->Album && defined $self->Track;
    return join $SEP,
        $self->Album,
        $self->Track,
        $str;
}

1;

__END__


=head1 NAME

Audio::MPD::Common::Item::Song - a song object with some audio tags


=head1 DESCRIPTION

C<Audio::MPD::Common::Item::Song> is more a placeholder for a
hash ref with some pre-defined keys, namely some audio tags.


=head1 PUBLIC METHODS

This module has a C<new()> constructor, which should only be called by
C<Audio::MPD::Common::Item>'s constructor.

The only other public methods are the accessors - see below.


=head2 Accessors

The following methods are the accessors to their respective named fields:
C<Album()>, C<Artist()>, C<file()>, C<id>, C<pos>, C<Title()>, CTTrack()>,
C<time()>. You can call them either with no arg to get the value, or with
an arg to replace the current value.


=head2 Methods


=over 4

=item $song->as_string()

Return a string representing $song. This string will be:

=over 4

=item either "Album = Track = Artist = Title"

=item or "Artist = Title"

=item or "Title"

=item or "file"

=back

(in this order), depending on the existing tags of the song. The last
possibility always exist of course, since it's a path.

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
