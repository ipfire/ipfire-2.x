#
# This file is part of Audio::MPD
# Copyright (c) 2007 Jerome Quelin, all rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself.
#
#

package Audio::MPD;

use warnings;
use strict;

use Audio::MPD::Collection;
use Audio::MPD::Common::Item;
use Audio::MPD::Common::Stats;
use Audio::MPD::Common::Status;
use Audio::MPD::Playlist;
use Encode;
use IO::Socket;
use Readonly;


use base qw[ Class::Accessor::Fast Exporter ];
__PACKAGE__->mk_accessors(
    qw[ _conntype _host _password _port _socket
        collection playlist version ] );


our $VERSION = '0.19.1';

Readonly our $REUSE => 1;
Readonly our $ONCE  => 0;

our @EXPORT = qw[ $REUSE $ONCE ];


#--
# Constructor

#
# my $mpd = Audio::MPD->new( [%opts] )
#
# This is the constructor for Audio::MPD. One can specify the following
# options:
#   - hostname => $hostname : defaults to environment var MPD_HOST, then to 'localhost'
#   - port     => $port     : defaults to env var MPD_PORT, then to 6600
#   - password => $password : defaults to env var MPD_PASSWORD, then to ''
#   - conntype => $type     : how the connection to mpd server is handled. it can be
#               either $REUSE: reuse the same connection
#                    or $ONCE: open a new connection per command (default)
#   
sub new {
    my ($class, %opts) = @_;

    # use mpd defaults.
    my ($default_password, $default_host) = split( '@', $ENV{MPD_HOST} )
       if exists $ENV{MPD_HOST} && $ENV{MPD_HOST} =~ /@/;
    my $host     = $opts{host}     || $default_host      || $ENV{MPD_HOST} || 'localhost';
    my $port     = $opts{port}     || $ENV{MPD_PORT}     || '6600';
    my $password = $opts{password} || $ENV{MPD_PASSWORD} || $default_password || '';

    # create & bless the object.
    my $self = {
        _host     => $host,
        _port     => $port,
        _password => $password,
        _conntype => exists $opts{conntype} ? $opts{conntype} : $ONCE,
    };
    bless $self, $class;

    # create the connection if conntype is set to $REUSE
    $self->_connect_to_mpd_server if $self->_conntype == $REUSE;


    # create the helper objects and store them.
    $self->collection( Audio::MPD::Collection->new($self) );
    $self->playlist  ( Audio::MPD::Playlist->new($self) );

    # try to issue a ping to test connection - this can die.
    $self->ping;

    return $self;
}


#--
# Private methods


#
# $mpd->_connect_to_mpd_server;
#
# This method connects to the mpd server. It can die on several conditions:
#  - if the server cannot be reached,
#  - if it's not an mpd server,
#  - or if the password is incorrect,
#
sub _connect_to_mpd_server {
    my ($self) = @_;

    # try to connect to mpd.
    my $socket = IO::Socket::INET->new(
        PeerAddr => $self->_host,
        PeerPort => $self->_port,
    )
    or die "Could not create socket: $!\n";

    # parse version information.
    my $line = $socket->getline;
    chomp $line;
    die "Not a mpd server - welcome string was: [$line]\n"
        if $line !~ /^OK MPD (.+)$/;
    $self->version($1);

    # send password.
    if ( $self->_password ) {
        $socket->print( 'password ' . encode('utf-8', $self->_password) . "\n" );
        $line = $socket->getline;
        die $line if $line =~ s/^ACK //;
    }

    # save socket
    $self->_socket($socket);
}


#
# my @result = $mpd->_send_command( $command );
#
# This method is central to the module. It is responsible for interacting with
# mpd by sending the $command and reading output - that will be returned as an
# array of chomped lines (status line will not be returned).
#
# This method can die on several conditions:
#  - if the server cannot be reached,
#  - if it's not an mpd server,
#  - if the password is incorrect,
#  - or if the command is an invalid mpd command.
# In the latter case, the mpd error message will be returned.
#
sub _send_command {
    my ($self, $command) = @_;

    $self->_connect_to_mpd_server if $self->_conntype == $ONCE;
    my $socket = $self->_socket;

    # ok, now we're connected - let's issue the command.
    $socket->print( encode('utf-8', $command) );
    my @output;
    while (defined ( my $line = $socket->getline ) ) {
        chomp $line;
        die $line if $line =~ s/^ACK //; # oops - error.
        last if $line =~ /^OK/;          # end of output.
        push @output, decode('utf-8', $line);
    }

    # close the socket.
    $socket->close if $self->_conntype == $ONCE;

    return @output;
}


#
# my @items = $mpd->_cooked_command_as_items( $command );
#
# Lots of Audio::MPD methods are using _send_command() and then parse the
# output as a collection of AMC::Item. This method is meant to factorize
# this code, and will parse the raw output of _send_command() in a cooked
# list of items.
#
sub _cooked_command_as_items {
    my ($self, $command) = @_;

    my @lines = $self->_send_command($command);
    my (@items, %param);

    # parse lines in reverse order since "file:" or "directory:" lines
    # come first. therefore, let's first store every other parameter,
    # and the last line will trigger the object creation.
    # of course, since we want to preserve the playlist order, this means
    # that we're going to unshift the objects instead of push.
    foreach my $line (reverse @lines) {
        my ($k,$v) = split /:\s/, $line, 2;
        $param{$k} = $v;
        next unless $k eq 'file' || $k eq 'directory' || $k eq 'playlist'; # last param of item
        unshift @items, Audio::MPD::Common::Item->new(%param);
        %param = ();
    }

    return @items;
}


sub _cooked_command_as_filename {
    my ($self, $command) = @_;

    my @lines = $self->_send_command($command);
    my (@items, %param);

    # parse lines in reverse order since "file:" or "directory:" lines
    # come first. therefore, let's first store every other parameter,
    # and the last line will trigger the object creation.
    # of course, since we want to preserve the playlist order, this means
    # that we're going to unshift the objects instead of push.
    foreach my $line (@lines) {
        my ($k,$v) = split /:\s/, $line, 2;
        if ( $k eq 'file'){$param{$k} = $v;}
        unshift @items, $param{'file'};
        %param = ();
    }

    return @items;
}

#
# my %hash = $mpd->_cooked_command_as_kv( $command );
#
# Lots of Audio::MPD methods are using _send_command() and then parse the
# output to get a list of key / value (with the colon ":" acting as separator).
# This method is meant to factorize this code, and will parse the raw output
# of _send_command() in a cooked hash.
#
sub _cooked_command_as_kv {
    my ($self, $command) = @_;
    my %hash =
        map { split(/:\s/, $_, 2) }
        $self->_send_command($command);
    return %hash;
}

#
# my @list = $mpd->_cooked_command_strip_first_field( $command );
#
# Lots of Audio::MPD methods are using _send_command() and then parse the
# output to remove the first field (with the colon ":" acting as separator).
# This method is meant to factorize this code, and will parse the raw output
# of _send_command() in a cooked list of strings.
#
sub _cooked_command_strip_first_field {
    my ($self, $command) = @_;

    my @list =
        map { ( split(/:\s+/, $_, 2) )[1] }
        $self->_send_command($command);
    return @list;
}


#--
# Public methods

# -- MPD interaction: general commands

#
# $mpd->ping;
#
# Sends a ping command to the mpd server.
#
sub ping {
    my ($self) = @_;
    $self->_send_command( "ping\n" );
}


#
# my $version = $mpd->version;
#
# Return version of MPD server's connected.
#
# sub version {} # implemented as an accessor.
#


#
# $mpd->kill;
#
# Send a message to the MPD server telling it to shut down.
#
sub kill {
    my ($self) = @_;
    $self->_send_command("kill\n");
}


#
# $mpd->password( [$password] )
#
# Change password used to communicate with MPD server to $password.
# Empty string is assumed if $password is not supplied.
#
sub password {
    my ($self, $passwd) = @_;
    $passwd ||= '';
    $self->_password($passwd);
    $self->ping; # ping sends a command, and thus the password is sent
}


#
# $mpd->updatedb( [$path] );
#
# Force mpd to rescan its collection. If $path (relative to MPD's music
# directory) is supplied, MPD will only scan it - otherwise, MPD will rescan
# its whole collection.
#
sub updatedb {
    my ($self, $path) = @_;
    $path ||= '';
    $self->_send_command("update $path\n");
}


#
# my @handlers = $mpd->urlhandlers;
#
# Return an array of supported URL schemes.
#
sub urlhandlers {
    my ($self) = @_;
    return $self->_cooked_command_strip_first_field("urlhandlers\n");
}


# -- MPD interaction: handling volume & output

#
# $mpd->volume( [+][-]$volume );
#
# Sets the audio output volume percentage to absolute $volume.
# If $volume is prefixed by '+' or '-' then the volume is changed relatively
# by that value.
#
sub volume {
    my ($self, $volume) = @_;

    if ($volume =~ /^(-|\+)(\d+)/ )  {
        my $current = $self->status->volume;
        $volume = $1 eq '+' ? $current + $2 : $current - $2;
    }
    $self->_send_command("setvol $volume\n");
}


#
# $mpd->output_enable( $output );
#
# Enable the specified audio output. $output is the ID of the audio output.
#
sub output_enable {
    my ($self, $output) = @_;
    $self->_send_command("enableoutput $output\n");
}


#
# $mpd->output_disable( $output );
#
# Disable the specified audio output. $output is the ID of the audio output.
#
sub output_disable {
    my ($self, $output) = @_;
    $self->_send_command("disableoutput $output\n");
}



# -- MPD interaction: retrieving info from current state

#
# $mpd->stats;
#
# Return an AMC::Stats object with the current statistics of MPD.
#
sub stats {
    my ($self) = @_;
    my %kv = $self->_cooked_command_as_kv( "stats\n" );
    return Audio::MPD::Common::Stats->new(\%kv);
}


#
# my $status = $mpd->status;
#
# Return an AMC::Status object with various information on current
# MPD server settings. Check the embedded pod for more information on the
# available accessors.
#
sub status {
    my ($self) = @_;
    my %kv = $self->_cooked_command_as_kv( "status\n" );
    my $status = Audio::MPD::Common::Status->new( \%kv );
    return $status;
}


#
# my $song = $mpd->current;
#
# Return an AMC::Item::Song representing the song currently playing.
#
sub current {
    my ($self) = @_;
    my ($item) = $self->_cooked_command_as_items("currentsong\n");
    return $item;
}


#
# my $song = $mpd->song( [$song] )
#
# Return an AMC::Item::Song representing the song number $song.
# If $song is not supplied, returns the current song.
#
sub song {
    my ($self, $song) = @_;
    return $self->current unless defined $song;
    my ($item) = $self->_cooked_command_as_items("playlistinfo $song\n");
    return $item;
}


#
# my $song = $mpd->songid( [$songid] )
#
# Return an AMC::Item::Song representing the song with id $songid.
# If $songid is not supplied, returns the current song.
#
sub songid {
    my ($self, $songid) = @_;
    return $self->current unless defined $songid;
    my ($item) = $self->_cooked_command_as_items("playlistid $songid\n");
    return $item;
}


# -- MPD interaction: altering settings

#
# $mpd->repeat( [$repeat] );
#
# Set the repeat mode to $repeat (1 or 0). If $repeat is not specified then
# the repeat mode is toggled.
#
sub repeat {
    my ($self, $mode) = @_;

    $mode = not $self->status->repeat
        unless defined $mode; # toggle if no param
    $mode = $mode ? 1 : 0;               # force integer
    $self->_send_command("repeat $mode\n");
}


#
# $mpd->random( [$random] );
#
# Set the random mode to $random (1 or 0). If $random is not specified then
# the random mode is toggled.
#
sub random {
    my ($self, $mode) = @_;

    $mode = not $self->status->random
        unless defined $mode; # toggle if no param
    $mode = $mode ? 1 : 0;               # force integer
    $self->_send_command("random $mode\n");
}


#
# $mpd->fade( [$seconds] );
#
# Enable crossfading and set the duration of crossfade between songs. If
# $seconds is not specified or $seconds is 0, then crossfading is disabled.
#
sub fade {
    my ($self, $value) = @_;
    $value ||= 0;
    $self->_send_command("crossfade $value\n");
}


# -- MPD interaction: controlling playback

#
# $mpd->play( [$song] );
#
# Begin playing playlist at song number $song. If no argument supplied,
# resume playing.
#
sub play {
    my ($self, $number) = @_;
    $number = '' unless defined $number;
    $self->_send_command("play $number\n");
}

#
# $mpd->playid( [$songid] );
#
# Begin playing playlist at song ID $songid. If no argument supplied,
# resume playing.
#
sub playid {
    my ($self, $number) = @_;
    $number ||= '';
    $self->_send_command("playid $number\n");
}


#
# $mpd->pause( [$sate] );
#
# Pause playback. If $state is 0 then the current track is unpaused, if
# $state is 1 then the current track is paused.
#
# Note that if $state is not given, pause state will be toggled.
#
sub pause {
    my ($self, $state) = @_;
    $state ||= ''; # default is to toggle
    $self->_send_command("pause $state\n");
}


#
# $mpd->stop;
#
# Stop playback.
#
sub stop {
    my ($self) = @_;
    $self->_send_command("stop\n");
}


#
# $mpd->next;
#
# Play next song in playlist.
#
sub next {
    my ($self) = @_;
    $self->_send_command("next\n");
}

#
# $mpd->prev;
#
# Play previous song in playlist.
#
sub prev {
    my($self) = shift;
    $self->_send_command("previous\n");
}


#
# $mpd->seek( $time, [$song] );
#
# Seek to $time seconds in song number $song. If $song number is not specified
# then the perl module will try and seek to $time in the current song.
#
sub seek {
    my ($self, $time, $song) = @_;
    $time ||= 0; $time = int $time;
    $song = $self->status->song if not defined $song; # seek in current song
    $self->_send_command( "seek $song $time\n" );
}


#
# $mpd->seekid( $time, [$songid] );
#
# Seek to $time seconds in song ID $songid. If $songid number is not specified
# then the perl module will try and seek to $time in the current song.
#
sub seekid {
    my ($self, $time, $song) = @_;
    $time ||= 0; $time = int $time;
    $song = $self->status->songid if not defined $song; # seek in current song
    $self->_send_command( "seekid $song $time\n" );
}


1;



__END__

=pod

=head1 NAME

Audio::MPD - class to talk to MPD (Music Player Daemon) servers


=head1 SYNOPSIS

    use Audio::MPD;

    my $mpd = Audio::MPD->new();
    $mpd->play();
    sleep 10;
    $mpd->next();


=head1 DESCRIPTION

Audio::MPD gives a clear object-oriented interface for talking to and
controlling MPD (Music Player Daemon) servers. A connection to the MPD
server is established as soon as a new Audio::MPD object is created.

Note that the module will by default connect to mpd before sending any
command, and will disconnect after the command has been issued. This scheme
is far from optimal, but allows us not to care about timeout disconnections.

B</!\> Note that Audio::MPD is using high-level, blocking sockets. This
means that if the mpd server is slow, or hangs for whatever reason, or
even crash abruptly, the program will be hung forever in this sub. The
POE::Component::Client::MPD module is way safer - you're advised to use
it instead of Audio::MPD. Or you can try to set C<conntype> to C<$REUSE>
(see Audio::MPD constructor for more details), but you would be then on
your own to deal with disconnections.


=head1 METHODS

=head2 Constructor

=over 4

=item new( [%opts] )

This is the constructor for Audio::MPD. One can specify the following
options:

=over 4

=item hostname => C<$hostname>

defaults to environment var MPD_HOST, then to 'localhost'. Note that
MPD_HOST can be of the form password@host.

=item port => C<$port>

defaults to environment var MPD_PORT, then to 6600.

=item password => $password

defaults to environment var MPD_PASSWORD, then to ''.

=item conntype => $type

change how the connection to mpd server is handled. It can be either
C<$REUSE> to reuse the same connection or C<$ONCE> to open a new
connection per command (default)

=back


=back


=head2 Controlling the server

=over 4

=item $mpd->ping()

Sends a ping command to the mpd server.


=item $mpd->version()

Return the version number for the server we are connected to.


=item $mpd->kill()

Send a message to the MPD server telling it to shut down.


=item $mpd->password( [$password] )

Change password used to communicate with MPD server to $password.
Empty string is assumed if $password is not supplied.


=item $mpd->updatedb( [$path] )

Force mpd to recan its collection. If $path (relative to MPD's music directory)
is supplied, MPD will only scan it - otherwise, MPD will rescan its whole
collection.


=item $mpd->urlhandlers()

Return an array of supported URL schemes.


=back


=head2 Handling volume & output

=over 4

=item $mpd->volume( [+][-]$volume )

Sets the audio output volume percentage to absolute $volume.
If $volume is prefixed by '+' or '-' then the volume is changed relatively
by that value.


=item $mpd->output_enable( $output )

Enable the specified audio output. $output is the ID of the audio output.


=item $mpd->output_disable( $output )

Disable the specified audio output. $output is the ID of the audio output.

=back


=head2 Retrieving info from current state

=over 4

=item $mpd->stats()

Return an C<Audio::MPD::Common::Stats> object with the current statistics
of MPD. See the associated pod for more information.


=item $mpd->status()

Return an C<Audio::MPD::Common::Status> object with various information on
current MPD server settings. Check the embedded pod for more information on
the available accessors.


=item $mpd->current()

Return an C<Audio::MPD::Common::Item::Song> representing the song currently
playing.


=item $mpd->song( [$song] )

Return an C<Audio::MPD::Common::Item::Song> representing the song number
C<$song>. If C<$song> is not supplied, returns the current song.


=item $mpd->songid( [$songid] )

Return an C<Audio::MPD::Common::Item::Song> representing the song with id
C<$songid>. If C<$songid> is not supplied, returns the current song.

=back


=head2 Altering MPD settings

=over 4

=item $mpd->repeat( [$repeat] )

Set the repeat mode to $repeat (1 or 0). If $repeat is not specified then
the repeat mode is toggled.


=item $mpd->random( [$random] )

Set the random mode to $random (1 or 0). If $random is not specified then
the random mode is toggled.


=item $mpd->fade( [$seconds] )

Enable crossfading and set the duration of crossfade between songs.
If $seconds is not specified or $seconds is 0, then crossfading is disabled.

=back


=head2 Controlling playback

=over 4

=item $mpd->play( [$song] )

Begin playing playlist at song number $song. If no argument supplied,
resume playing.


=item $mpd->playid( [$songid] )

Begin playing playlist at song ID $songid. If no argument supplied,
resume playing.


=item $mpd->pause( [$state] )

Pause playback. If C<$state> is 0 then the current track is unpaused,
if $state is 1 then the current track is paused.

Note that if C<$state> is not given, pause state will be toggled.


=item $mpd->stop()

Stop playback.


=item $mpd->next()

Play next song in playlist.


=item $mpd->prev()

Play previous song in playlist.


=item $mpd->seek( $time, [$song])

Seek to $time seconds in song number $song. If $song number is not specified
then the perl module will try and seek to $time in the current song.


=item $mpd->seekid( $time, $songid )

Seek to $time seconds in song ID $songid. If $song number is not specified
then the perl module will try and seek to $time in the current song.

=back


=head2 Searching the collection

To search the collection, use the C<collection()> accessor, returning the
associated C<Audio::MPD::Collection> object. You will then be able to call:

    $mpd->collection->random_song();

See C<Audio::MPD::Collection> documentation for more details on available
methods.


=head2 Handling the playlist

To update the playlist, use the C<playlist()> accessor, returning the
associated C<Audio::MPD::Playlist> object. You will then be able to call:

    $mpd->playlist->clear;

See C<Audio::MPD::Playlist> documentation for more details on available
methods.


=head1 SEE ALSO

You can find more information on the mpd project on its homepage at
L<http://www.musicpd.org>, or its wiki L<http://mpd.wikia.com>.

Regarding this Perl module, you can report bugs on CPAN via
L<http://rt.cpan.org/Public/Bug/Report.html?Queue=Audio-MPD>.

Audio::MPD development takes place on <audio-mpd@googlegroups.com>: feel free
to join us. (use L<http://groups.google.com/group/audio-mpd> to sign in). Our
subversion repository is located at L<https://svn.musicpd.org>.


=head1 AUTHOR

Jerome Quelin, C<< <jquelin at cpan.org> >>

Original code by Tue Abrahamsen C<< <tue.abrahamsen at gmail.com> >>,
documented by Nicholas J. Humfrey C<< <njh at aelius.com> >>.


=head1 COPYRIGHT & LICENSE

Copyright (c) 2005 Tue Abrahamsen, all rights reserved.
Copyright (c) 2006 Nicolas J. Humfrey, all rights reserved.
Copyright (c) 2007 Jerome Quelin, all rights reserved.

This program is free software; you can redistribute it and/or modify
it under the same terms as Perl itself.

=cut
