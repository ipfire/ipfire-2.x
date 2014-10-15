#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2014  IPFire Team  <alexander.marx@ipfire.org>                #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################


use DBI;

###############################################################################
my $dbh;
my $dsn="dbi:SQLite:dbname=/var/ipfire/accounting/acct.db";
###############################################################################


$dbh = DBI->connect($dsn, "", "",{RaiseError => 1, AutoCommit => 1})or die "ERROR $!";

$dbh->do('CREATE TABLE ACCT        (TIME_RUN "NUM",NAME "TXT",BYTES "NUM");');

$dbh->do('CREATE TABLE ACCT_HIST   (TIME_RUN "NUM",NAME "TXT",BYTES "NUM");');

$dbh->do('CREATE TABLE ACCT_ADDR   (COMPANY "TXT",TYPE "TXT",NAME1 "TXT", STR "TXT", NR "TXT", POSTCODE "NUM", CITY "TXT",BANK "TXT",IBAN "TXT",BIC "TXT",BLZ "NUM",ACCOUNT "NUM", EMAIL "TXT",INTERNET "TXT", HRB "TXT", USTID "TXT", TEL "TXT", FAX "TXT", CCMAIL "TXT");');

$dbh->do('CREATE TABLE BILLINGGRP  (NAME "TXT",BILLTEXT "TXT",HOST "TXT",CUST "TXT",CENT "NUM");');

$dbh->do('CREATE TABLE BILLINGHOST (GRP "TXT",HOST "TXT");');

$dbh->do('CREATE TABLE BILLPOS     (GRP "TXT",AMOUNT "INT", POS "TXT", PRICE "NUM");');

$dbh->do('CREATE TABLE BILLS       (NO "NUM", PATH "TXT", NAME "TXT", DATE "NUM", GRP "TXT");');

$dbh->disconnect();

exit 0;
