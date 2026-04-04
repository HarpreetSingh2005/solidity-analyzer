// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract NoExternalCall {
    uint public value;

    function update(uint x) public {
        value = x;
    }
}
