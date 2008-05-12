#
# This file is part of Audio::MPD::Common
# Copyright (c) 2007 Jerome Quelin, all rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself.
#
#

package Audio::MPD::Common::Status;

use warnings;
use strict;

use Audio::MPD::Common::Time;

use base qw[ Class::Accessor::Fast ];
__PACKAGE__->mk_accessors
    ( qw[ audio bitrate error playlist playlistlength random
          repeat song songid state time volume updating_db xfade ] );

#our ($VERSION) = '$Rev: 5865 $' =~ /(\d+)/;


#--
# Constructor

#
# my $status = Audio::MPD::Common::Status->new( \%kv )
#
# The constructor for the class Audio::MPD::Common::Status. %kv is
# a cooked output of what MPD server returns to the status command.
#
sub new {
    my ($class, $kv) = @_;
    my %kv = %$kv;
    $kv{time} = Audio::MPD::Common::Time->new( delete $kv{time} );
    bless \%kv, $class;
    return \%kv;
}

1;

__END__


=head1 NAME

Audio::MPD::Common::Status - class representing MPD status


=head1 SYNOPSIS

    print $status->bitrate;


=head1 DESCRIPTION

The MPD server maintains some information on its current state. Those
information can be queried with mpd modules. Some of those information
are served to you as an C<Audio::MPD::Common::Status> object.

Note that an C<Audio::MPD::Common::Status> object does B<not> update
itself regularly, and thus should be used immediately.


=head1 METHODS

=head2 Constructor

=over 4

=item new( \%kv )

The C<new()> method is the constructor for the C<Audio::MPD::Common::Status>
class.

Note: one should B<never> ever instantiate an C<Audio::MPD::Common::Status>
object directly - use the mpd modules instead.

=back


=head2 Accessors

Once created, one can access to the following members of the object:

=over 4

=item $status->audio()

A string with the sample rate of the song currently playing, number of bits
of the output and number of channels (2 for stereo) - separated by a colon.


=item $status->bitrate()

The instantaneous bitrate in kbps.


=item $status->error()

May appear in special error cases, such as when disabling output.


=item $status->playlist()

The playlist version number, that changes every time the playlist is updated.


=item $status->playlistlength()

The number of songs in the playlist.


=item $status->random()

Whether the playlist is read randomly or not.


=item $status->repeat()

Whether the song is repeated or not.


=item $status->song()

The offset of the song currently played in the playlist.


=item $status->songid()

The song id (MPD id) of the song currently played.


=item $status->state()

The state of MPD server. Either C<play>, C<stop> or C<pause>.


=item $status->time()

An C<Audio::MPD::Common::Time> object, representing the time elapsed /
remainging and total. See the associated pod for more details.


=item $status->updating_db()

An integer, representing the current update job.


=item $status->volume()

The current MPD volume - an integer between 0 and 100.


=item $status->xfade()

The crossfade in seconds.


=back

Please note that those accessors are read-only: changing a value will B<not>
change the current settings of MPD server. Use the mpd modules to alter the
settings.


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
