// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Unbounded loop can cause out of gas error (DoS).
contract VulnNewInfiniteLoop {
    address[] public users;
    function distribute() external {
        for(uint i=0; i<users.length; i++) {
            // If users array grows too large, this will always OOG
        }
    }
}