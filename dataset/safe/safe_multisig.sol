// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeMultisig {
    address[] public owners;
    uint256 public required;

    constructor(address[] memory _owners, uint256 _required) {
        owners = _owners;
        required = _required;
    }
}