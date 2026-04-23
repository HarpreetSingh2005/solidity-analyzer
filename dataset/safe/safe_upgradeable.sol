// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeUpgradeable {
    address public implementation;
    address public admin;

    constructor(address _impl) {
        implementation = _impl;
        admin = msg.sender;
    }

    function upgrade(address newImpl) public {
        require(msg.sender == admin, "Not admin");
        implementation = newImpl;
    }
}