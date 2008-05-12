#
# This file is part of Audio::MPD::Common
# Copyright (c) 2007 Jerome Quelin, all rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself.
#
#

package Audio::MPD::Common::Item::Directory;

use strict;
use warnings;

use base qw[ Class::Accessor::Fast Audio::MPD::Common::Item ];
__PACKAGE__->mk_accessors( qw[ directory ] );

#our ($VERSION) = '$Rev: 5645 $' =~ /(\d+)/;

1;

__END__


=head1 NAME

Audio::MPD::Common::Item::Directory - a directory object


=head1 SYNOPSIS

    print $item->directory . "\n";


=head1 DESCRIPTION

C<Audio::MPD::Common::Item::Directory> is more a placeholder for a
hash ref with one pre-defined key, namely the directory name.


=head1 PUBLIC METHODS

This module only has a C<new()> constructor, which should only be called by
C<Audio::MPD::Common::Item>'s constructor.

The only other public method is an accessor: directory().


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
