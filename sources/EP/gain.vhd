library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity gain is
    port(
        -- global
        i_clk_slow           : in  std_logic;
        i_reset              : in  std_logic;
        -- input gain       
        i_gain               : in  unsigned(31 downto 0);
        -- input data
        i_data_after_filter  : in  signed(15 downto 0);
        i_ready_after_filter : in  std_logic;
        -- output data
        o_data_after_gain    : out signed(15 downto 0);
        o_ready_after_gain   : out std_logic
    );
end entity gain;

architecture RTL of gain is

begin

    label_gain : process(i_clk_slow, i_reset) is
    begin
        if i_reset = '1' then
            o_data_after_gain  <= (others => '0');
            o_ready_after_gain <= '0';
        elsif rising_edge(i_clk_slow) then
            o_ready_after_gain <= '0';
            if i_ready_after_filter = '1' then
                o_ready_after_gain <= '1';
                o_data_after_gain  <= SHIFT_LEFT(i_data_after_filter, To_integer(i_gain));
            end if;
        end if;
    end process;

end architecture RTL;
