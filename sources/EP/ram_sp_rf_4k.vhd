library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.UT_EGSE_EP_Package.all;

entity ram_sp_rf_4k is
    port(
        reset  : in  std_logic;
        i_clk  : in  std_logic;
        i_we   : in  std_logic;
        i_en   : in  std_logic;
        i_addr : in  std_logic_vector(11 downto 0);
        i_di   : in  std_logic_vector(15 downto 0);
        o_do   : out std_logic_vector(15 downto 0)
    );
end entity ram_sp_rf_4k;

architecture RTL of ram_sp_rf_4k is

    type Array_config_15stdx4_type is array (3 downto 0) of std_logic_vector(15 downto 0);
    type Array_config_10stdx4_type is array (3 downto 0) of std_logic_vector(9 downto 0);

    signal addr         : Array_config_10stdx4_type;
    signal di           : Array_config_15stdx4_type;
    signal do           : Array_config_15stdx4_type;
    signal MSB_addr     : std_logic_vector(1 downto 0);
    signal MSB_addr_old : std_logic_vector(1 downto 0);
    signal we           : std_logic_vector(3 downto 0);
    signal en           : std_logic_vector(3 downto 0);

begin

    ------------------------------------------
    --  EP
    ------------------------------------------
    generate_rams_sp_rf : for N IN 3 downto 0 generate
        label_rams_sp_rf : entity work.rams_sp_rf
            port map(
                clk  => i_clk,
                we   => we(N),
                en   => en(N),
                addr => addr(N),
                di   => di(N),
                do   => do(N)
            );
    end generate generate_rams_sp_rf;

    we(0) <= i_we and not i_addr(11) and not i_addr(10);
    we(1) <= i_we and not i_addr(11) and i_addr(10);
    we(2) <= i_we and i_addr(11) and not i_addr(10);
    we(3) <= i_we and i_addr(11) and i_addr(10);

    en(0) <= i_en and not i_addr(11) and not i_addr(10);
    en(1) <= i_en and not i_addr(11) and i_addr(10);
    en(2) <= i_en and i_addr(11) and not i_addr(10);
    en(3) <= i_en and i_addr(11) and i_addr(10);

    addr(0) <= i_addr(9 downto 0);
    addr(1) <= i_addr(9 downto 0);
    addr(2) <= i_addr(9 downto 0);
    addr(3) <= i_addr(9 downto 0);

    di(0) <= i_di;
    di(1) <= i_di;
    di(2) <= i_di;
    di(3) <= i_di;

    --MSB_addr <= i_addr(11) & i_addr(10);

    label_process : process(i_clk, reset) is
    begin
        if reset = '1' then
            MSB_addr_old <= (others => '0');
        elsif rising_edge(i_clk) then
            MSB_addr_old <= i_addr(11) & i_addr(10);
        end if;
    end process;

    --    --------------------------------------------------------------------------
    --    o_do     <= do(0) when MSB_addr_old = "00" else
    --                do(1) when MSB_addr_old = "01" else
    --                do(2) when MSB_addr_old = "10" else
    --                do(3) when MSB_addr_old = "11";

    ------------------------------------------
    --  wire out for FIFO pipe out science, wire out for FIFO pipe out spectrum
    ------------------------------------------

    label_process_inter_wire : process(i_clk, reset) is
    begin
        if reset = '1' then
            o_do <= (others => '0');
        elsif rising_edge(i_clk) then
            if MSB_addr_old = "00" then
                o_do <= do(0);
            elsif MSB_addr_old = "01" then
                o_do <= do(1);

            elsif MSB_addr_old = "10" then
                o_do <= do(2);
            elsif MSB_addr_old = "11" then
                o_do <= do(3);
            end if;
        end if;
    end process;

end architecture RTL;
