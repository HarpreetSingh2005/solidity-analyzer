// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UncheckedCalls {
    function sendEth(address payable target) public {
        // Vulnerable: return value of low-level call is not checked
        target.call{value: 1 ether}("");
    }
}
