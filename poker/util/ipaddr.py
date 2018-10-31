# -*- coding: utf-8 -*-
"""

This library is used to create/poke/manipulate IPv4 and IPv6 addresses
and networks.

"""
__version__ = '2.1.11'
import struct
IPV4LENGTH = 32
IPV6LENGTH = 128

class AddressValueError(ValueError, ):
    """

    """

class NetmaskValueError(ValueError, ):
    """

    """

def IPAddress(address, version=None):
    """

    Args:
        address: A string or integer, the IP address.  Either IPv4 or
          IPv6 addresses may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.
        version: An Integer, 4 or 6. If set, don't try to automatically
          determine what the IP address type is. important for things
          like IPAddress(1), which could be IPv4, '0.0.0.1',  or IPv6,
          '::1'.

    Returns:
        An IPv4Address or IPv6Address object.

    Raises:
        ValueError: if the string passed isn't either a v4 or a v6
          address.

    """
    pass

def IPNetwork(address, version=None, strict=False):
    """

    Args:
        address: A string or integer, the IP address.  Either IPv4 or
          IPv6 addresses may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.
        version: An Integer, if set, don't try to automatically
          determine what the IP address type is. important for things
          like IPNetwork(1), which could be IPv4, '0.0.0.1/32', or IPv6,
          '::1/128'.

    Returns:
        An IPv4Network or IPv6Network object.

    Raises:
        ValueError: if the string passed isn't either a v4 or a v6
          address. Or if a strict network was requested and a strict
          network wasn't given.

    """
    pass

def v4_int_to_packed(address):
    """

    Args:
        address: An integer representation of an IPv4 IP address.

    Returns:
        The binary representation of this address.

    Raises:
        ValueError: If the integer is too large to be an IPv4 IP
          address.
    """
    pass

def v6_int_to_packed(address):
    """

    Args:
        address: An integer representation of an IPv6 IP address.

    Returns:
        The binary representation of this address.
    """
    pass

def _find_address_range(addresses):
    """

    Args:
        addresses: a list of IPv4 or IPv6 addresses.

    Returns:
        A tuple containing the first and last IP addresses in the sequence.

    """
    pass

def _get_prefix_length(number1, number2, bits):
    """

    Args:
        number1: an integer.
        number2: another integer.
        bits: the maximum number of bits to compare.

    Returns:
        The number of leading bits that are the same for two numbers.

    """
    pass

def _count_righthand_zero_bits(number, bits):
    """

    Args:
        number: an integer.
        bits: maximum number of bits to count.

    Returns:
        The number of zero bits on the right hand side of the number.

    """
    pass

def summarize_address_range(first, last):
    """

    Example:
        >>> summarize_address_range(IPv4Address('1.1.1.0'),
            IPv4Address('1.1.1.130'))
        [IPv4Network('1.1.1.0/25'), IPv4Network('1.1.1.128/31'),
        IPv4Network('1.1.1.130/32')]

    Args:
        first: the first IPv4Address or IPv6Address in the range.
        last: the last IPv4Address or IPv6Address in the range.

    Returns:
        The address range collapsed to a list of IPv4Network's or
        IPv6Network's.

    Raise:
        TypeError:
            If the first and last objects are not IP addresses.
            If the first and last objects are not the same version.
        ValueError:
            If the last object is not greater than the first.
            If the version is not 4 or 6.

    """
    pass

def _collapse_address_list_recursive(addresses):
    """

    Example:

        ip1 = IPv4Network('1.1.0.0/24')
        ip2 = IPv4Network('1.1.1.0/24')
        ip3 = IPv4Network('1.1.2.0/24')
        ip4 = IPv4Network('1.1.3.0/24')
        ip5 = IPv4Network('1.1.4.0/24')
        ip6 = IPv4Network('1.1.0.1/22')

        _collapse_address_list_recursive([ip1, ip2, ip3, ip4, ip5, ip6]) ->
          [IPv4Network('1.1.0.0/22'), IPv4Network('1.1.4.0/24')]

        This shouldn't be called directly; it is called via
          collapse_address_list([]).

    Args:
        addresses: A list of IPv4Network's or IPv6Network's

    Returns:
        A list of IPv4Network's or IPv6Network's depending on what we were
        passed.

    """
    pass

def collapse_address_list(addresses):
    """

    Example:
        collapse_address_list([IPv4('1.1.0.0/24'), IPv4('1.1.1.0/24')]) ->
          [IPv4('1.1.0.0/23')]

    Args:
        addresses: A list of IPv4Network or IPv6Network objects.

    Returns:
        A list of IPv4Network or IPv6Network objects depending on what we
        were passed.

    Raises:
        TypeError: If passed a list of mixed version objects.

    """
    pass
CollapseAddrList = collapse_address_list
try:
    if (bytes is str):
        raise TypeError('bytes is not a distinct type')
    Bytes = bytes
except (NameError, TypeError):

    class Bytes(str, ):

        def __repr__(self):
            pass

def get_mixed_type_key(obj):
    """

    Address and Network objects are not sortable by default; they're
    fundamentally different so the expression

        IPv4Address('1.1.1.1') <= IPv4Network('1.1.1.1/24')

    doesn't make any sense.  There are some times however, where you may wish
    to have ipaddr sort these for you anyway. If you need to do this, you
    can use this function as the key= argument to sorted().

    Args:
      obj: either a Network or Address object.
    Returns:
      appropriate key.

    """
    pass

class _IPAddrBase(object, ):
    """

    """

    def __index__(self):
        pass

    def __int__(self):
        pass

    def __hex__(self):
        pass

    @property
    def exploded(self):
        """

        """
        pass

    @property
    def compressed(self):
        """

        """
        pass

class _BaseIP(_IPAddrBase, ):
    """

    This IP class contains the version independent methods which are
    used by single IP addresses.

    """

    def __eq__(self, other):
        pass

    def __ne__(self, other):
        pass

    def __le__(self, other):
        pass

    def __ge__(self, other):
        pass

    def __lt__(self, other):
        pass

    def __gt__(self, other):
        pass

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __hash__(self):
        pass

    def _get_address_key(self):
        pass

    @property
    def version(self):
        pass

class _BaseNet(_IPAddrBase, ):
    """

    This IP class contains the version independent methods which are
    used by networks.

    """

    def __init__(self, address):
        pass

    def __repr__(self):
        pass

    def iterhosts(self):
        """

           This is like __iter__ except it doesn't return the network
           or broadcast addresses.

        """
        pass

    def __iter__(self):
        pass

    def __getitem__(self, n):
        pass

    def __lt__(self, other):
        pass

    def __gt__(self, other):
        pass

    def __le__(self, other):
        pass

    def __ge__(self, other):
        pass

    def __eq__(self, other):
        pass

    def __ne__(self, other):
        pass

    def __str__(self):
        pass

    def __hash__(self):
        pass

    def __contains__(self, other):
        pass

    def overlaps(self, other):
        """

        """
        pass

    @property
    def network(self):
        pass

    @property
    def broadcast(self):
        pass

    @property
    def hostmask(self):
        pass

    @property
    def with_prefixlen(self):
        pass

    @property
    def with_netmask(self):
        pass

    @property
    def with_hostmask(self):
        pass

    @property
    def numhosts(self):
        """

        """
        pass

    @property
    def version(self):
        pass

    @property
    def prefixlen(self):
        pass

    def address_exclude(self, other):
        """

        For example:

            addr1 = IPNetwork('10.1.1.0/24')
            addr2 = IPNetwork('10.1.1.0/26')
            addr1.address_exclude(addr2) =
                [IPNetwork('10.1.1.64/26'), IPNetwork('10.1.1.128/25')]

        or IPv6:

            addr1 = IPNetwork('::1/32')
            addr2 = IPNetwork('::1/128')
            addr1.address_exclude(addr2) = [IPNetwork('::0/128'),
                IPNetwork('::2/127'),
                IPNetwork('::4/126'),
                IPNetwork('::8/125'),
                ...
                IPNetwork('0:0:8000::/33')]

        Args:
            other: An IPvXNetwork object of the same type.

        Returns:
            A sorted list of IPvXNetwork objects addresses which is self
            minus other.

        Raises:
            TypeError: If self and other are of difffering address
              versions, or if other is not a network object.
            ValueError: If other is not completely contained by self.

        """
        pass

    def compare_networks(self, other):
        """

        This is only concerned about the comparison of the integer
        representation of the network addresses.  This means that the
        host bits aren't considered at all in this method.  If you want
        to compare host bits, you can easily enough do a
        'HostA._ip < HostB._ip'

        Args:
            other: An IP object.

        Returns:
            If the IP versions of self and other are the same, returns:

            -1 if self < other:
              eg: IPv4('1.1.1.0/24') < IPv4('1.1.2.0/24')
              IPv6('1080::200C:417A') < IPv6('1080::200B:417B')
            0 if self == other
              eg: IPv4('1.1.1.1/24') == IPv4('1.1.1.2/24')
              IPv6('1080::200C:417A/96') == IPv6('1080::200C:417B/96')
            1 if self > other
              eg: IPv4('1.1.1.0/24') > IPv4('1.1.0.0/24')
              IPv6('1080::1:200C:417A/112') >
              IPv6('1080::0:200C:417A/112')

            If the IP versions of self and other are different, returns:

            -1 if self._version < other._version
              eg: IPv4('10.0.0.1/24') < IPv6('::1/128')
            1 if self._version > other._version
              eg: IPv6('::1/128') > IPv4('255.255.255.0/24')

        """
        pass

    def _get_networks_key(self):
        """

        Returns an object that identifies this address' network and
        netmask. This function is a suitable "key" argument for sorted()
        and list.sort().

        """
        pass

    def _ip_int_from_prefix(self, prefixlen):
        """

        Args:
            prefixlen: An integer, the prefix length.

        Returns:
            An integer.

        """
        pass

    def _prefix_from_ip_int(self, ip_int):
        """

        Args:
            ip_int: An integer, the netmask in expanded bitwise format.

        Returns:
            An integer, the prefix length.

        Raises:
            NetmaskValueError: If the input is not a valid netmask.

        """
        pass

    def _prefix_from_prefix_string(self, prefixlen_str):
        """

        Args:
            prefixlen_str: A decimal string containing the prefix length.

        Returns:
            The prefix length as an integer.

        Raises:
            NetmaskValueError: If the input is malformed or out of range.

        """
        pass

    def _prefix_from_ip_string(self, ip_str):
        """

        Args:
            ip_str: A netmask or hostmask, formatted as an IP address.

        Returns:
            The prefix length as an integer.

        Raises:
            NetmaskValueError: If the input is not a netmask or hostmask.

        """
        pass

    def iter_subnets(self, prefixlen_diff=1, new_prefix=None):
        """

        In the case that self contains only one IP
        (self._prefixlen == 32 for IPv4 or self._prefixlen == 128
        for IPv6), return a list with just ourself.

        Args:
            prefixlen_diff: An integer, the amount the prefix length
              should be increased by. This should not be set if
              new_prefix is also set.
            new_prefix: The desired new prefix length. This must be a
              larger number (smaller prefix) than the existing prefix.
              This should not be set if prefixlen_diff is also set.

        Returns:
            An iterator of IPv(4|6) objects.

        Raises:
            ValueError: The prefixlen_diff is too small or too large.
                OR
            prefixlen_diff and new_prefix are both set or new_prefix
              is a smaller number than the current prefix (smaller
              number means a larger network)

        """
        pass

    def masked(self):
        """

        """
        pass

    def subnet(self, prefixlen_diff=1, new_prefix=None):
        """

        """
        pass

    def supernet(self, prefixlen_diff=1, new_prefix=None):
        """

        Args:
            prefixlen_diff: An integer, the amount the prefix length of
              the network should be decreased by.  For example, given a
              /24 network and a prefixlen_diff of 3, a supernet with a
              /21 netmask is returned.

        Returns:
            An IPv4 network object.

        Raises:
            ValueError: If self.prefixlen - prefixlen_diff < 0. I.e., you have a
              negative prefix length.
                OR
            If prefixlen_diff and new_prefix are both set or new_prefix is a
              larger number than the current prefix (larger number means a
              smaller network)

        """
        pass
    Subnet = subnet
    Supernet = supernet
    AddressExclude = address_exclude
    CompareNetworks = compare_networks
    Contains = __contains__

class _BaseV4(object, ):
    """

    The following methods are used by IPv4 objects in both single IP
    addresses and networks.

    """
    _ALL_ONES = ((2 ** IPV4LENGTH) - 1)
    _DECIMAL_DIGITS = frozenset('0123456789')

    def __init__(self, address):
        pass

    def _explode_shorthand_ip_string(self):
        pass

    def _ip_int_from_string(self, ip_str):
        """

        Args:
            ip_str: A string, the IP ip_str.

        Returns:
            The IP ip_str as an integer.

        Raises:
            AddressValueError: if ip_str isn't a valid IPv4 Address.

        """
        pass

    def _parse_octet(self, octet_str):
        """

        Args:
            octet_str: A string, the number to parse.

        Returns:
            The octet as an integer.

        Raises:
            ValueError: if the octet isn't strictly a decimal from [0..255].

        """
        pass

    def _string_from_ip_int(self, ip_int):
        """

        Args:
            ip_int: An integer, the IP address.

        Returns:
            The IP address as a string in dotted decimal notation.

        """
        pass

    @property
    def max_prefixlen(self):
        pass

    @property
    def packed(self):
        """

        """
        pass

    @property
    def version(self):
        pass

    @property
    def is_reserved(self):
        """

        Returns:
            A boolean, True if the address is within the
            reserved IPv4 Network range.

        """
        pass

    @property
    def is_private(self):
        """

        Returns:
            A boolean, True if the address is reserved per RFC 1918.

        """
        pass

    @property
    def is_multicast(self):
        """

        Returns:
            A boolean, True if the address is multicast.
            See RFC 3171 for details.

        """
        pass

    @property
    def is_unspecified(self):
        """

        Returns:
            A boolean, True if this is the unspecified address as defined in
            RFC 5735 3.

        """
        pass

    @property
    def is_loopback(self):
        """

        Returns:
            A boolean, True if the address is a loopback per RFC 3330.

        """
        pass

    @property
    def is_link_local(self):
        """

        Returns:
            A boolean, True if the address is link-local per RFC 3927.

        """
        pass

class IPv4Address(_BaseV4, _BaseIP, ):
    """

    """

    def __init__(self, address):
        """
        Args:
            address: A string or integer representing the IP
              '192.168.1.1'

              Additionally, an integer can be passed, so
              IPv4Address('192.168.1.1') == IPv4Address(3232235777).
              or, more generally
              IPv4Address(int(IPv4Address('192.168.1.1'))) ==
                IPv4Address('192.168.1.1')

        Raises:
            AddressValueError: If ipaddr isn't a valid IPv4 address.

        """
        pass

class IPv4Network(_BaseV4, _BaseNet, ):
    """

    Attributes: [examples for IPv4Network('1.2.3.4/27')]
        ._ip: 16909060
        .ip: IPv4Address('1.2.3.4')
        .network: IPv4Address('1.2.3.0')
        .hostmask: IPv4Address('0.0.0.31')
        .broadcast: IPv4Address('1.2.3.31')
        .netmask: IPv4Address('255.255.255.224')
        .prefixlen: 27

    """

    def __init__(self, address, strict=False):
        """

        Args:
            address: A string or integer representing the IP [& network].
              '192.168.1.1/24'
              '192.168.1.1/255.255.255.0'
              '192.168.1.1/0.0.0.255'
              are all functionally the same in IPv4. Similarly,
              '192.168.1.1'
              '192.168.1.1/255.255.255.255'
              '192.168.1.1/32'
              are also functionaly equivalent. That is to say, failing to
              provide a subnetmask will create an object with a mask of /32.

              If the mask (portion after the / in the argument) is given in
              dotted quad form, it is treated as a netmask if it starts with a
              non-zero field (e.g. /255.0.0.0 == /8) and as a hostmask if it
              starts with a zero field (e.g. 0.255.255.255 == /8), with the
              single exception of an all-zero mask which is treated as a
              netmask == /0. If no mask is given, a default of /32 is used.

              Additionally, an integer can be passed, so
              IPv4Network('192.168.1.1') == IPv4Network(3232235777).
              or, more generally
              IPv4Network(int(IPv4Network('192.168.1.1'))) ==
                IPv4Network('192.168.1.1')

            strict: A boolean. If true, ensure that we have been passed
              A true network address, eg, 192.168.1.0/24 and not an
              IP address on a network, eg, 192.168.1.1/24.

        Raises:
            AddressValueError: If ipaddr isn't a valid IPv4 address.
            NetmaskValueError: If the netmask isn't valid for
              an IPv4 address.
            ValueError: If strict was True and a network address was not
              supplied.

        """
        pass
    IsRFC1918 = (lambda self: self.is_private)
    IsMulticast = (lambda self: self.is_multicast)
    IsLoopback = (lambda self: self.is_loopback)
    IsLinkLocal = (lambda self: self.is_link_local)

class _BaseV6(object, ):
    """

    The following methods are used by IPv6 objects in both single IP
    addresses and networks.

    """
    _ALL_ONES = ((2 ** IPV6LENGTH) - 1)
    _HEXTET_COUNT = 8
    _HEX_DIGITS = frozenset('0123456789ABCDEFabcdef')

    def __init__(self, address):
        pass

    def _ip_int_from_string(self, ip_str):
        """

        Args:
            ip_str: A string, the IPv6 ip_str.

        Returns:
            A long, the IPv6 ip_str.

        Raises:
            AddressValueError: if ip_str isn't a valid IPv6 Address.

        """
        pass

    def _parse_hextet(self, hextet_str):
        """

        Args:
            hextet_str: A string, the number to parse.

        Returns:
            The hextet as an integer.

        Raises:
            ValueError: if the input isn't strictly a hex number from [0..FFFF].

        """
        pass

    def _compress_hextets(self, hextets):
        """

        Compresses a list of strings, replacing the longest continuous
        sequence of "0" in the list with "" and adding empty strings at
        the beginning or at the end of the string such that subsequently
        calling ":".join(hextets) will produce the compressed version of
        the IPv6 address.

        Args:
            hextets: A list of strings, the hextets to compress.

        Returns:
            A list of strings.

        """
        pass

    def _string_from_ip_int(self, ip_int=None):
        """

        Args:
            ip_int: An integer, the IP address.

        Returns:
            A string, the hexadecimal representation of the address.

        Raises:
            ValueError: The address is bigger than 128 bits of all ones.

        """
        pass

    def _explode_shorthand_ip_string(self):
        """

        Args:
            ip_str: A string, the IPv6 address.

        Returns:
            A string, the expanded IPv6 address.

        """
        pass

    @property
    def max_prefixlen(self):
        pass

    @property
    def packed(self):
        """

        """
        pass

    @property
    def version(self):
        pass

    @property
    def is_multicast(self):
        """

        Returns:
            A boolean, True if the address is a multicast address.
            See RFC 2373 2.7 for details.

        """
        pass

    @property
    def is_reserved(self):
        """

        Returns:
            A boolean, True if the address is within one of the
            reserved IPv6 Network ranges.

        """
        pass

    @property
    def is_unspecified(self):
        """

        Returns:
            A boolean, True if this is the unspecified address as defined in
            RFC 2373 2.5.2.

        """
        pass

    @property
    def is_loopback(self):
        """

        Returns:
            A boolean, True if the address is a loopback address as defined in
            RFC 2373 2.5.3.

        """
        pass

    @property
    def is_link_local(self):
        """

        Returns:
            A boolean, True if the address is reserved per RFC 4291.

        """
        pass

    @property
    def is_site_local(self):
        """

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test if this address is in the space of unique local
        addresses as defined by RFC 4193.

        Returns:
            A boolean, True if the address is reserved per RFC 3513 2.5.6.

        """
        pass

    @property
    def is_private(self):
        """

        Returns:
            A boolean, True if the address is reserved per RFC 4193.

        """
        pass

    @property
    def ipv4_mapped(self):
        """

        Returns:
            If the IPv6 address is a v4 mapped address, return the
            IPv4 mapped address. Return None otherwise.

        """
        pass

    @property
    def teredo(self):
        """

        Returns:
            Tuple of the (server, client) IPs or None if the address
            doesn't appear to be a teredo address (doesn't start with
            2001::/32)

        """
        pass

    @property
    def sixtofour(self):
        """

        Returns:
            The IPv4 6to4-embedded address if present or None if the
            address doesn't appear to contain a 6to4 embedded address.

        """
        pass

class IPv6Address(_BaseV6, _BaseIP, ):
    """

    """

    def __init__(self, address):
        """

        Args:
            address: A string or integer representing the IP

              Additionally, an integer can be passed, so
              IPv6Address('2001:4860::') ==
                IPv6Address(42541956101370907050197289607612071936L).
              or, more generally
              IPv6Address(IPv6Address('2001:4860::')._ip) ==
                IPv6Address('2001:4860::')

        Raises:
            AddressValueError: If address isn't a valid IPv6 address.

        """
        pass

class IPv6Network(_BaseV6, _BaseNet, ):
    """

    Attributes: [examples for IPv6('2001:658:22A:CAFE:200::1/64')]
        .ip: IPv6Address('2001:658:22a:cafe:200::1')
        .network: IPv6Address('2001:658:22a:cafe::')
        .hostmask: IPv6Address('::ffff:ffff:ffff:ffff')
        .broadcast: IPv6Address('2001:658:22a:cafe:ffff:ffff:ffff:ffff')
        .netmask: IPv6Address('ffff:ffff:ffff:ffff::')
        .prefixlen: 64

    """

    def __init__(self, address, strict=False):
        """

        Args:
            address: A string or integer representing the IPv6 network or the IP
              and prefix/netmask.
              '2001:4860::/128'
              '2001:4860:0000:0000:0000:0000:0000:0000/128'
              '2001:4860::'
              are all functionally the same in IPv6.  That is to say,
              failing to provide a subnetmask will create an object with
              a mask of /128.

              Additionally, an integer can be passed, so
              IPv6Network('2001:4860::') ==
                IPv6Network(42541956101370907050197289607612071936L).
              or, more generally
              IPv6Network(IPv6Network('2001:4860::')._ip) ==
                IPv6Network('2001:4860::')

            strict: A boolean. If true, ensure that we have been passed
              A true network address, eg, 192.168.1.0/24 and not an
              IP address on a network, eg, 192.168.1.1/24.

        Raises:
            AddressValueError: If address isn't a valid IPv6 address.
            NetmaskValueError: If the netmask isn't valid for
              an IPv6 address.
            ValueError: If strict was True and a network address was not
              supplied.

        """
        pass

    @property
    def with_netmask(self):
        pass